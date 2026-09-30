"""Streaming, regenerate, feedback, language detection, DB migration, home page."""
import json
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class FakeLlama:
    """Mimics llama_cpp.Llama.create_chat_completion(stream=True/False)."""
    def __init__(self):
        self.calls = []

    def create_chat_completion(self, messages, stream=False, **kw):
        self.calls.append(messages)
        words = ["Use ", "Flask ", "and ", "SQLite."]
        if stream:
            return ({"choices": [{"delta": {"content": w}}]} for w in words)
        return {"choices": [{"message": {"content": "".join(words)}}]}


@pytest.fixture()
def env(tmp_path, monkeypatch):
    from backend import ai, auth, config, database
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "t.db")
    fake = FakeLlama()
    monkeypatch.setattr(ai, "load_model", lambda: fake)
    monkeypatch.setattr(ai, "_llm", None)
    from backend.main import app
    database.init_db(); auth.ensure_admin_account()
    app.config["TESTING"] = True
    c = app.test_client()
    c.post("/signup", data={"name": "Sakshi Dhaker", "email": "s@x.com", "password": "secret1"})
    return c, fake


def events(resp):
    out = []
    for block in resp.get_data(as_text=True).split("\n\n"):
        if block.startswith("data: "):
            out.append(json.loads(block[6:]))
    return out


def test_streaming_tokens_and_saved(env):
    c, fake = env
    ev = events(c.post("/api/chat/stream", json={"message": "Which stack for a login app?"}))
    assert ev[0]["type"] == "meta" and ev[0]["chat_id"]
    assert "".join(e["text"] for e in ev if e["type"] == "token") == "Use Flask and SQLite."
    assert ev[-1]["type"] == "done" and ev[-1]["message_id"]
    msgs = c.get(f"/api/chats/{ev[0]['chat_id']}").get_json()["messages"]
    assert [m["role"] for m in msgs] == ["user", "assistant"] and msgs[1]["content"] == "Use Flask and SQLite."


def test_regenerate_replaces_last_answer(env):
    c, fake = env
    cid = events(c.post("/api/chat/stream", json={"message": "hello there"}))[0]["chat_id"]
    ev = events(c.post("/api/chat/stream", json={"chat_id": cid, "regenerate": True}))
    assert ev[-1]["type"] == "done"
    msgs = c.get(f"/api/chats/{cid}").get_json()["messages"]
    assert [m["role"] for m in msgs] == ["user", "assistant"]          # not 3 messages


def test_regenerate_without_answer_is_error(env):
    c, _ = env
    assert c.post("/api/chat/stream", json={"regenerate": True}).status_code == 400


def test_feedback_and_owner_only(env):
    c, _ = env
    ev = events(c.post("/api/chat/stream", json={"message": "hi"}))
    mid, cid = ev[-1]["message_id"], ev[0]["chat_id"]
    assert c.post("/api/feedback", json={"message_id": mid, "value": 1}).status_code == 200
    assert c.get(f"/api/chats/{cid}").get_json()["messages"][1]["feedback"] == 1
    assert c.post("/api/feedback", json={"message_id": mid, "value": 5}).status_code == 404
    c.post("/logout")
    c.post("/signup", data={"name": "Other Person", "email": "o@x.com", "password": "secret1"})
    assert c.post("/api/feedback", json={"message_id": mid, "value": -1}).status_code == 404


def test_language_instruction_reaches_model(env):
    c, fake = env
    events(c.post("/api/chat/stream", json={"message": "Mujhe Flask me login kaise banana hai?"}))
    assert "Hinglish" in fake.calls[-1][-1]["content"]
    events(c.post("/api/chat/stream", json={"message": "फ्लास्क में लॉगिन कैसे बनाएं"}))
    assert "Devanagari" in fake.calls[-1][-1]["content"]
    events(c.post("/api/chat/stream", json={"message": "How do I build a login page?"}))
    assert "English" in fake.calls[-1][-1]["content"]


def test_language_detection_samples():
    from backend.lang import detect_language as d
    assert d("Give me 5 project ideas in machine learning") == "english"
    assert d("mughe project idea batao") == "hinglish"
    assert d("React aur Node me login kaise banate hain") == "hinglish"
    assert d("मुझे प्रोजेक्ट आइडिया बताओ") == "hindi"
    assert d("Explain RAG in English") == "english"


def test_hinglish_query_finds_english_knowledge():
    from backend import rag
    hits = rag.search_knowledge("mujhe machine learning project idea batao", k=3)
    assert hits and any("Machine Learning" in h["title"] or "Project Ideas" in h["title"] for h in hits)


def test_no_model_streams_knowledge_fallback(tmp_path, monkeypatch):
    from backend import ai, auth, config, database
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "n.db"); monkeypatch.setattr(database, "DB_PATH", tmp_path / "n.db")
    monkeypatch.setattr(ai, "load_model", lambda: None); monkeypatch.setattr(ai, "_llm", None)
    from backend.main import app
    database.init_db(); auth.ensure_admin_account(); app.config["TESTING"] = True
    c = app.test_client(); c.post("/signup", data={"name": "Sakshi D", "email": "s@x.com", "password": "secret1"})
    ev = events(c.post("/api/chat/stream", json={"message": "what should my project report contain"}))
    assert ev[-1]["type"] == "done" and ev[-1]["engine"] == "knowledge-only"


def test_old_database_gets_feedback_column(tmp_path, monkeypatch):
    from backend import config, database
    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.executescript("""CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, created_at TEXT);
    CREATE TABLE chats(id INTEGER PRIMARY KEY, user_id INT, title TEXT, created_at TEXT, updated_at TEXT);
    CREATE TABLE messages(id INTEGER PRIMARY KEY, chat_id INT, role TEXT, content TEXT, sources TEXT, created_at TEXT);
    INSERT INTO users VALUES(1,'A','a@a.com','x','t'); INSERT INTO chats VALUES(1,1,'old chat','t','t');
    INSERT INTO messages VALUES(1,1,'user','hi',NULL,'t');""")
    conn.commit(); conn.close()
    monkeypatch.setattr(database, "DB_PATH", path)
    database.init_db()
    assert database.get_messages(1)[0]["feedback"] == 0


def test_home_page_for_logged_in_user_and_admin_feedback_stats(env):
    c, _ = env
    r = c.get("/")
    assert r.status_code == 200 and b"Open chat" in r.data
    ev = events(c.post("/api/chat/stream", json={"message": "hi"}))
    c.post("/api/feedback", json={"message_id": ev[-1]["message_id"], "value": 1})
    c.post("/logout"); c.post("/login", data={"email": "admin@local.test", "password": "admin"})
    assert c.get("/admin").status_code == 200
