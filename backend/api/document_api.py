"""Create Artifact: RAG -> Qwen -> validator (one retry) -> PDF/DOCX."""
import re
import uuid

from flask import Blueprint, jsonify, request, session

from backend import ai, rag
from backend.lang import detect_language
from backend.auth import login_required
from backend.config import GENERATED_DIR
from backend.docx_generator import build_docx
from backend.pdf_generator import build_pdf
from backend.validator import validate_generated

bp = Blueprint("document", __name__)

DOC_RULES = ("Write a complete, well-structured document in Markdown with a clear title, headings (##), "
             "bullet points and, when useful, fenced code blocks. Do not add chatty introductions.")


@bp.route("/api/generate", methods=["POST"])
@login_required
def generate():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    fmt = data.get("format", "pdf")
    if len(prompt) < 5:
        return jsonify({"error": "Describe what document you want."}), 400
    if fmt not in ("pdf", "docx"):
        return jsonify({"error": "Format must be pdf or docx."}), 400

    results = rag.search_knowledge(prompt, k=5)
    context = rag.get_context(results, max_chars=3000)
    messages = ai.build_chat_messages(f"{DOC_RULES}\n\nRequest: {prompt}", context, lang=detect_language(prompt))
    text, engine = ai.generate_text(messages, max_tokens=900)
    if text is None:
        text = ai.fallback_answer(results)
    else:
        ok, problem = validate_generated(text)
        if not ok:                                    # one retry with feedback
            messages.append({"role": "assistant", "content": text})
            messages.append({"role": "user", "content": f"Problem: {problem} Rewrite the full document."})
            text, engine = ai.generate_text(messages, max_tokens=900)

    title = re.sub(r"\s+", " ", prompt)[:70].strip().capitalize()
    name = f"u{session['user_id']}_{uuid.uuid4().hex[:10]}.{fmt}"
    path = GENERATED_DIR / name
    (build_pdf if fmt == "pdf" else build_docx)(title, text, path)
    return jsonify({"file": name, "url": f"/download/{name}", "preview": text[:1200], "engine": engine})
