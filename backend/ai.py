"""Local Qwen (llama-cpp-python): download, load, prompt, generate.

If the model cannot run (missing package / download failed) the app still answers
from the retrieved knowledge, so the demo never shows a blank error.
"""
import threading

from backend.lang import language_directive

from backend.config import MAX_TOKENS, MODEL_FILE, MODEL_LABEL, MODEL_REPO, MODELS_DIR, N_CTX

STATE = {"status": "idle", "message": "Model not loaded yet"}
_llm = None
_load_lock = threading.Lock()
_gen_lock = threading.Lock()          # llama.cpp handles one generation at a time

SYSTEM_PROMPT = (
    "You are Technical Planning Assistant, a friendly senior mentor for engineering students. "
    "You help with project ideas, tech-stack choice, architecture, database design, API design, "
    "step-by-step implementation, roadmaps, reports and viva preparation. You also answer normal "
    "general and technical questions.\n"
    "You can plan full-stack projects in ANY language or framework (Python, JavaScript/Node/React, Java/Spring, "
    "PHP/Laravel, C#/.NET, Go, Dart/Flutter, C/C++...). For a project question use this order: "
    "1) what it is, 2) tech stack, 3) folder structure, 4) database tables, 5) API endpoints, "
    "6) build steps in order, 7) a short code example.\n"
    "Rules:\n"
    "- Use the CONTEXT below when it is relevant; do not copy it blindly.\n"
    "- If the context does not cover the question, answer from general knowledge and say when you are unsure.\n"
    "- Follow the language instruction at the end of the student's message exactly.\n"
    "- Explain simply, like to a beginner: short headings, bullet points, numbered steps, small code blocks.\n"
    "- Never invent libraries, functions or facts."
)


def _find_model_file():
    for p in MODELS_DIR.glob("*.gguf"):
        if p.name.lower() == MODEL_FILE.lower():
            return str(p)
    return None


def ensure_model_downloaded():
    path = _find_model_file()
    if path:
        return path
    STATE.update(status="downloading", message="Downloading Qwen model (about 490 MB)...")
    from huggingface_hub import hf_hub_download
    return hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILE, local_dir=str(MODELS_DIR))


def load_model():
    """Load Qwen once. Returns the Llama object or None when unavailable."""
    global _llm
    if _llm is not None:
        return _llm
    with _load_lock:
        if _llm is not None:
            return _llm
        try:
            path = ensure_model_downloaded()
            STATE.update(status="loading", message="Loading model into memory...")
            from llama_cpp import Llama
            import os
            _llm = Llama(model_path=path, n_ctx=N_CTX, n_threads=os.cpu_count() or 4, verbose=False)
            STATE.update(status="ready", message=f"{MODEL_LABEL} ready")
        except Exception as exc:
            STATE.update(status="error", message=f"{exc.__class__.__name__}: {exc}"[:220])
            _llm = None
    return _llm


def warm_up():
    threading.Thread(target=load_model, daemon=True).start()


def build_chat_messages(question, context, history=None, lang=None):
    system = SYSTEM_PROMPT + ("\n\nCONTEXT:\n" + context if context else "\n\nCONTEXT: (nothing relevant found)")
    msgs = [{"role": "system", "content": system}]
    for m in (history or [])[-6:]:
        msgs.append({"role": m["role"], "content": m["content"][:1500]})
    user_text = question
    if lang:
        user_text += "\n\n(" + language_directive(lang) + ")"
    msgs.append({"role": "user", "content": user_text})
    return msgs


def get_llm():
    """Return the loaded model, or None. Never blocks while a download/load is in progress."""
    if _llm is not None:
        return _llm
    if STATE["status"] in ("downloading", "loading"):
        return None
    return load_model()


def generate_text(messages, max_tokens=MAX_TOKENS, temperature=0.4):
    """Return (text, engine). engine is 'qwen' or 'knowledge-only'."""
    llm = get_llm()
    if llm is None:
        return None, "knowledge-only"
    with _gen_lock:
        out = llm.create_chat_completion(messages=messages, max_tokens=max_tokens,
                                         temperature=temperature, top_p=0.9, repeat_penalty=1.1)
    return out["choices"][0]["message"]["content"].strip(), "qwen"


def stream_text(messages, max_tokens=MAX_TOKENS, temperature=0.4):
    """Yield the answer piece by piece. Yields nothing when the model is unavailable."""
    llm = get_llm()
    if llm is None:
        return
    with _gen_lock:
        for chunk in llm.create_chat_completion(messages=messages, max_tokens=max_tokens, temperature=temperature,
                                                top_p=0.9, repeat_penalty=1.1, stream=True):
            piece = chunk["choices"][0].get("delta", {}).get("content")
            if piece:
                yield piece


def fallback_answer(results):
    """Used only when Qwen is not available: show the best knowledge found."""
    loading = STATE["status"] in ("downloading", "loading")
    note = ("The local model is still loading, so here is the closest note from the knowledge base"
            if loading else "The local model is not running, so here is the closest note from the knowledge base")
    if not results:
        return (f"{note.split(',')[0]}. I found nothing in the knowledge base for this yet. "
                "Wait for the green dot in the sidebar and ask again.")
    best = results[0]
    return f"**{note} ({best['title']}):**\n\n{best['text']}"


def status():
    return {**STATE, "label": MODEL_LABEL}
