"""Password rules, session helpers and the admin account."""
import re
from functools import wraps

from flask import jsonify, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from backend import database
from backend.config import ADMIN_EMAIL, ADMIN_PASSWORD

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_signup(name, email, password):
    """Return an error message, or None when everything is fine."""
    if len(name.strip()) < 2:
        return "Please enter your full name."
    if not EMAIL_RE.match(email):
        return "Please enter a valid email address."
    if len(password) < 6:
        return "Password must be at least 6 characters."
    return None


def hash_password(password):
    return generate_password_hash(password)


def verify_password(stored_hash, password):
    return check_password_hash(stored_hash, password)


def current_user():
    uid = session.get("user_id")
    return database.get_user(uid) if uid else None


def is_admin(user):
    return bool(user) and user["email"] == ADMIN_EMAIL


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id") or not current_user():
            session.clear()
            if request.path.startswith("/api/"):
                return jsonify({"error": "Please log in again."}), 401
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapper


def ensure_admin_account():
    """Create/refresh the demo admin so the admin login always works."""
    user = database.get_user_by_email(ADMIN_EMAIL)
    if user is None:
        database.create_user("Admin", ADMIN_EMAIL, hash_password(ADMIN_PASSWORD))
    elif not verify_password(user["password"], ADMIN_PASSWORD):
        database.update_user_password(user["id"], hash_password(ADMIN_PASSWORD))
