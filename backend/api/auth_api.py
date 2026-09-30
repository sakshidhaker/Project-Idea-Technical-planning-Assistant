"""Signup / login / logout routes."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from backend import auth, database

bp = Blueprint("auth", __name__)


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("app_page"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        error = auth.validate_signup(name, email, password)
        if error:
            flash(error, "error")
            return render_template("signup.html", name=name, email=email)
        if database.get_user_by_email(email):
            flash("This email is already registered. Please log in.", "info")
            return redirect(url_for("auth.login", email=email))
        uid = database.create_user(name, email, auth.hash_password(password))
        session.clear()
        session["user_id"] = uid          # new user goes straight to the chat home
        return redirect(url_for("app_page"))
    return render_template("signup.html", name="", email="")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("app_page"))
    email = (request.form.get("email") or request.args.get("email") or "").strip().lower()
    if request.method == "POST":
        user = database.get_user_by_email(email)
        if user and auth.verify_password(user["password"], request.form.get("password", "")):
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("app_page"))
        flash("Wrong email or password. New here? Create an account.", "error")
    return render_template("login.html", email=email)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("landing"))
