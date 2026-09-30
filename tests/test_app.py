import importlib, os, sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    from backend import config
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "t.db")
    from backend import database
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "t.db")
    from backend import ai
    monkeypatch.setattr(ai, "load_model", lambda: None)      # test without the real model
    from backend.main import app
    database.init_db()
    from backend import auth
    auth.ensure_admin_account()
    app.config["TESTING"] = True
    return app.test_client()


def signup(c, email="a@b.com"):
    return c.post("/signup", data={"name": "Sakshi Dhaker", "email": email, "password": "secret1"})


def test_pages_and_redirects(client):
    assert client.get("/").status_code == 200
    assert client.get("/app").status_code == 302          # not logged in
    assert client.get("/api/chats").status_code == 401


def test_signup_goes_home_and_duplicate_goes_login(client):
    r = signup(client)
    assert r.status_code == 302 and r.headers["Location"].endswith("/app")
    assert b"Sakshi" in client.get("/app").data
    client.post("/logout")
    r = signup(client)
    assert "/login" in r.headers["Location"]


def test_login_wrong_and_right(client):
    signup(client); client.post("/logout")
    assert b"Wrong email" in client.post("/login", data={"email": "a@b.com", "password": "nope"}).data
    r = client.post("/login", data={"email": "a@b.com", "password": "secret1"})
    assert r.headers["Location"].endswith("/app")


def test_chat_history_flow(client):
    signup(client)
    d = client.post("/api/chat", json={"message": "Give me a machine learning project idea"}).get_json()
    assert d["chat_id"] and d["reply"] and d["sources"]
    d2 = client.post("/api/chat", json={"message": "roadmap for 8 weeks", "chat_id": d["chat_id"]}).get_json()
    assert d2["chat_id"] == d["chat_id"]
    assert len(client.get("/api/chats").get_json()) == 1
    assert len(client.get(f"/api/chats/{d['chat_id']}").get_json()["messages"]) == 4
    assert len(client.get("/api/chats?q=roadmap").get_json()) == 1
    client.delete(f"/api/chats/{d['chat_id']}")
    assert client.get("/api/chats").get_json() == []


def test_users_cannot_read_each_others_chats(client):
    signup(client, "one@x.com")
    cid = client.post("/api/chat", json={"message": "hello project"}).get_json()["chat_id"]
    client.post("/logout"); signup(client, "two@x.com")
    assert client.get(f"/api/chats/{cid}").status_code == 404


@pytest.mark.parametrize("fmt", ["pdf", "docx"])
def test_generate_and_download(client, fmt):
    signup(client)
    d = client.post("/api/generate", json={"prompt": "Project proposal for heart disease prediction", "format": fmt}).get_json()
    r = client.get(d["url"])
    assert r.status_code == 200 and len(r.data) > 1000


def test_admin_only(client):
    signup(client)
    assert client.get("/admin").status_code == 302
    client.post("/logout")
    client.post("/login", data={"email": "admin@local.test", "password": "admin"})
    r = client.get("/admin")
    assert r.status_code == 200 and b"a@b.com" in r.data
