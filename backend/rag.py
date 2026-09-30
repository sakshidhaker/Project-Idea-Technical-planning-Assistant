"""RAG: load knowledge/*.txt -> chunk -> embed -> search.

Uses Sentence-Transformers embeddings when available. If the embedding model
cannot be loaded (offline / not installed) it falls back to TF-IDF so the app
never breaks. Add or edit a .txt file in knowledge/ and the index rebuilds itself.
"""
import re
import threading

import numpy as np

from backend.lang import expand_query

from backend.config import EMBED_MODEL, KNOWLEDGE_DIR, RAG_BACKEND

_lock = threading.Lock()
_index = {"signature": None, "chunks": [], "matrix": None, "kind": None, "vec": None, "model": None}


def load_knowledge():
    docs = []
    for path in sorted(KNOWLEDGE_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        if text:
            docs.append((path.name, text))
    return docs


def split_documents(docs, max_chars=750):
    """Split on blank lines, then merge small paragraphs. Each chunk keeps its title."""
    chunks = []
    for name, text in docs:
        lines = text.splitlines()
        title = lines[0].lstrip("# ").strip() if lines else name
        buf = ""
        for para in re.split(r"\n\s*\n", text):
            para = para.strip()
            if not para:
                continue
            if buf and len(buf) + len(para) > max_chars:
                chunks.append({"source": name, "title": title, "text": buf.strip()})
                buf = ""
            buf += para + "\n\n"
        if buf.strip():
            chunks.append({"source": name, "title": title, "text": buf.strip()})
    return chunks


def _signature():
    return tuple((p.name, p.stat().st_mtime_ns) for p in sorted(KNOWLEDGE_DIR.glob("*.txt")))


def _build():
    chunks = split_documents(load_knowledge())
    texts = [f"{c['title']}. {c['text']}" for c in chunks]
    _index.update(chunks=chunks, matrix=None, kind=None, vec=None)
    if not texts:
        return
    if RAG_BACKEND in ("auto", "semantic"):
        try:
            from sentence_transformers import SentenceTransformer
            if _index["model"] is None:
                _index["model"] = SentenceTransformer(EMBED_MODEL)
            _index["matrix"] = np.asarray(
                _index["model"].encode(texts, normalize_embeddings=True, show_progress_bar=False))
            _index["kind"] = "semantic"
            return
        except Exception as exc:  # offline, missing package, ...
            print(f"[rag] semantic embeddings unavailable ({exc.__class__.__name__}); using TF-IDF")
            if RAG_BACKEND == "semantic":
                raise
    from sklearn.feature_extraction.text import TfidfVectorizer
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    _index["matrix"] = vec.fit_transform(texts)
    _index["vec"] = vec
    _index["kind"] = "tfidf"


def _ensure_index():
    sig = _signature()
    with _lock:
        if _index["signature"] != sig:
            _build()
            _index["signature"] = sig


def search_knowledge(query, k=4):
    """Return up to k chunks: [{source, title, text, score}]."""
    _ensure_index()
    query = expand_query(query)
    if _index["matrix"] is None or not _index["chunks"]:
        return []
    with _lock:
        if _index["kind"] == "semantic":
            q = _index["model"].encode([query], normalize_embeddings=True, show_progress_bar=False)[0]
            scores = _index["matrix"] @ q
            floor = 0.28
        else:
            q = _index["vec"].transform([query])
            scores = (_index["matrix"] @ q.T).toarray().ravel()
            floor = 0.08
        chunks = _index["chunks"]
    order = np.argsort(scores)[::-1][:k]
    return [{**chunks[i], "score": round(float(scores[i]), 3)} for i in order if scores[i] >= floor]


def get_context(results, max_chars=2400):
    parts, used = [], 0
    for r in results:
        block = f"[{r['title']}]\n{r['text']}"
        if used + len(block) > max_chars:
            break
        parts.append(block)
        used += len(block)
    return "\n\n".join(parts)


def index_info():
    _ensure_index()
    return {"chunks": len(_index["chunks"]), "files": len({c["source"] for c in _index["chunks"]}),
            "engine": _index["kind"]}
