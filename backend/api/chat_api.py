"""Chat endpoints: normal + streaming answers, regenerate, feedback, history."""
import json
import time

from flask import Blueprint, Response, jsonify, request, session

from backend import ai, database, rag
from backend.auth import login_required
from backend.lang import detect_language

bp = Blueprint("chat", __name__)


def _prepare(uid, data):
    """Shared by /api/chat and /api/chat/stream. Returns (error, chat_id, messages, sources, results)."""
    chat_id = data.get("chat_id")
    if chat_id and not database.get_chat(uid, chat_id):
        chat_id = None

    if data.get("regenerate") and chat_id:            # answer the last question again
        question, history = database.pop_last_answer(chat_id)
        if not question:
            return ("Nothing to regenerate yet.", None, None, None, None)
    else:
        question = (data.get("message") or "").strip()[:2000]
        if not question:
            return ("Please type a question.", None, None, None, None)
        if not chat_id:
            chat_id = database.create_chat(uid, question)
        history = database.get_messages(chat_id, limit=12)
        database.add_message(chat_id, "user", question)

    lang = detect_language(question)
    results = rag.search_knowledge(question, k=4)
    messages = ai.build_chat_messages(question, rag.get_context(results), history, lang)
    sources = [{"title": r["title"], "file": r["source"], "score": r["score"]} for r in results[:3]]
    return (None, chat_id, messages, sources, results)


@bp.route("/api/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    error, chat_id, messages, sources, results = _prepare(session["user_id"], data)
    if error:
        return jsonify({"error": error}), 400
    reply, engine = ai.generate_text(messages)
    if reply is None:
        reply = ai.fallback_answer(results)
    mid = database.add_message(chat_id, "assistant", reply, sources)
    return jsonify({"chat_id": chat_id, "reply": reply, "sources": sources, "engine": engine, "message_id": mid})


def _sse(obj):
    return "data: " + json.dumps(obj, ensure_ascii=False) + "\n\n"


@bp.route("/api/chat/stream", methods=["POST"])
@login_required
def chat_stream():
    data = request.get_json(silent=True) or {}
    error, chat_id, messages, sources, results = _prepare(session["user_id"], data)
    if error:
        return jsonify({"error": error}), 400

    def generate():
        parts, saved = [], False
        try:
            yield _sse({"type": "meta", "chat_id": chat_id, "sources": sources})
            engine = "qwen"
            try:
                for piece in ai.stream_text(messages):
                    parts.append(piece)
                    yield _sse({"type": "token", "text": piece})
            except Exception as exc:                       # model crashed mid-answer
                if not parts:
                    parts = []
                yield _sse({"type": "error", "message": f"Model error: {exc.__class__.__name__}"})
            if not parts:                                   # no model -> show the knowledge instead
                engine = "knowledge-only"
                words = ai.fallback_answer(results).split(" ")
                for i in range(0, len(words), 5):
                    chunk = " ".join(words[i:i + 5]) + " "
                    parts.append(chunk)
                    yield _sse({"type": "token", "text": chunk})
                    time.sleep(0.02)
            mid = database.add_message(chat_id, "assistant", "".join(parts).strip(), sources)
            saved = True
            yield _sse({"type": "done", "message_id": mid, "engine": engine})
        finally:
            if not saved and parts:                         # user pressed Stop: keep what was written
                database.add_message(chat_id, "assistant", "".join(parts).strip(), sources)

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@bp.route("/api/feedback", methods=["POST"])
@login_required
def feedback():
    data = request.get_json(silent=True) or {}
    try:
        mid, value = int(data.get("message_id")), int(data.get("value", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Bad request"}), 400
    if value not in (-1, 0, 1) or not database.set_feedback(session["user_id"], mid, value):
        return jsonify({"error": "Message not found"}), 404
    return jsonify({"ok": True, "value": value})


@bp.route("/api/chats")
@login_required
def chats():
    return jsonify(database.list_chats(session["user_id"], request.args.get("q", "")))


@bp.route("/api/chats/<int:chat_id>")
@login_required
def open_chat(chat_id):
    chat = database.get_chat(session["user_id"], chat_id)
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
    return jsonify({"id": chat["id"], "title": chat["title"], "messages": database.get_messages(chat_id)})


@bp.route("/api/chats/<int:chat_id>", methods=["DELETE"])
@login_required
def remove_chat(chat_id):
    database.delete_chat(session["user_id"], chat_id)
    return jsonify({"ok": True})


@bp.route("/api/status")
@login_required
def status():
    return jsonify({"model": ai.status(), "rag": rag.index_info()})
