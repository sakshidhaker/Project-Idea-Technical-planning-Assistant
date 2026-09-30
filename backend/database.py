"""All SQLite code lives here: users, chats, messages."""
import json
import sqlite3
from datetime import datetime

from backend.config import DB_PATH


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            sources TEXT,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_chats_user ON chats(user_id, updated_at);
        CREATE INDEX IF NOT EXISTS idx_msgs_chat ON messages(chat_id, id);
        """)
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(messages)")]
        if "feedback" not in cols:                     # older databases get the new column
            conn.execute("ALTER TABLE messages ADD COLUMN feedback INTEGER NOT NULL DEFAULT 0")


# ---------- users ----------
def create_user(name, email, password_hash):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO users (name, email, password, created_at) VALUES (?,?,?,?)",
            (name, email, password_hash, now()))
        return cur.lastrowid


def get_user_by_email(email):
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def get_user(user_id):
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def update_user_password(user_id, password_hash):
    with get_db() as conn:
        conn.execute("UPDATE users SET password = ? WHERE id = ?", (password_hash, user_id))


def list_users(search=""):
    like = f"%{search.strip()}%"
    with get_db() as conn:
        return conn.execute("""
            SELECT u.id, u.name, u.email, u.created_at,
                   (SELECT COUNT(*) FROM chats c WHERE c.user_id = u.id) AS chat_count
            FROM users u WHERE u.name LIKE ? OR u.email LIKE ? ORDER BY u.id DESC""",
            (like, like)).fetchall()


def delete_user(user_id):
    with get_db() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))


# ---------- chats ----------
def create_chat(user_id, title):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO chats (user_id, title, created_at, updated_at) VALUES (?,?,?,?)",
            (user_id, title[:60], now(), now()))
        return cur.lastrowid


def list_chats(user_id, search=""):
    like = f"%{search.strip()}%"
    with get_db() as conn:
        rows = conn.execute("""
            SELECT DISTINCT c.id, c.title, c.updated_at FROM chats c
            LEFT JOIN messages m ON m.chat_id = c.id
            WHERE c.user_id = ? AND (c.title LIKE ? OR m.content LIKE ?)
            ORDER BY c.updated_at DESC, c.id DESC LIMIT 100""",
            (user_id, like, like)).fetchall()
        return [dict(r) for r in rows]


def get_chat(user_id, chat_id):
    with get_db() as conn:
        return conn.execute("SELECT * FROM chats WHERE id = ? AND user_id = ?",
                            (chat_id, user_id)).fetchone()


def delete_chat(user_id, chat_id):
    with get_db() as conn:
        conn.execute("DELETE FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id))


def add_message(chat_id, role, content, sources=None):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO messages (chat_id, role, content, sources, created_at) VALUES (?,?,?,?,?)",
            (chat_id, role, content, json.dumps(sources) if sources else None, now()))
        conn.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now(), chat_id))
        return cur.lastrowid


def get_messages(chat_id, limit=200):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, role, content, sources, feedback, created_at FROM messages WHERE chat_id = ? ORDER BY id LIMIT ?",
            (chat_id, limit)).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["sources"] = json.loads(d["sources"]) if d["sources"] else []
        out.append(d)
    return out


def pop_last_answer(chat_id):
    """For Regenerate: delete the last assistant message. Return (question, history) or (None, [])."""
    msgs = get_messages(chat_id, limit=500)
    if not msgs or msgs[-1]["role"] != "assistant":
        return None, []
    with get_db() as conn:
        conn.execute("DELETE FROM messages WHERE id = ?", (msgs[-1]["id"],))
    msgs = msgs[:-1]
    if not msgs or msgs[-1]["role"] != "user":
        return None, []
    return msgs[-1]["content"], msgs[:-1]


def set_feedback(user_id, message_id, value):
    """value: 1 = thumbs up, -1 = thumbs down, 0 = cleared. Only the chat owner can rate."""
    with get_db() as conn:
        cur = conn.execute("""UPDATE messages SET feedback = ?
            WHERE id = ? AND role = 'assistant'
              AND chat_id IN (SELECT id FROM chats WHERE user_id = ?)""", (value, message_id, user_id))
        return cur.rowcount > 0


# ---------- admin ----------
def stats():
    with get_db() as conn:
        one = lambda q: conn.execute(q).fetchone()[0]
        return {"users": one("SELECT COUNT(*) FROM users"),
                "chats": one("SELECT COUNT(*) FROM chats"),
                "messages": one("SELECT COUNT(*) FROM messages"),
                "likes": one("SELECT COUNT(*) FROM messages WHERE feedback = 1"),
                "dislikes": one("SELECT COUNT(*) FROM messages WHERE feedback = -1")}


def recent_messages(limit=25):
    with get_db() as conn:
        return conn.execute("""
            SELECT m.id, u.name, u.email, c.title, m.role, m.content, m.created_at
            FROM messages m JOIN chats c ON c.id = m.chat_id JOIN users u ON u.id = c.user_id
            ORDER BY m.id DESC LIMIT ?""", (limit,)).fetchall()
