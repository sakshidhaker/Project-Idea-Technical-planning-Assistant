"""Flask app: pages, blueprints, startup."""
from flask import Flask, redirect, render_template, request, session, url_for

from backend import admin, ai, auth, database
from backend.api import auth_api, chat_api, document_api, downloads_api
from backend.config import MODEL_LABEL, SECRET_KEY

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
app.secret_key = SECRET_KEY
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

for module in (auth_api, chat_api, document_api, downloads_api):
    app.register_blueprint(module.bp)

database.init_db()
auth.ensure_admin_account()


@app.route("/")
def landing():
    return render_template("landing.html", model=MODEL_LABEL, logged_in=bool(session.get("user_id")))


@app.route("/app")
@auth.login_required
def app_page():
    user = auth.current_user()
    return render_template("app.html", user=user, is_admin=auth.is_admin(user), model=MODEL_LABEL)


@app.route("/admin", methods=["GET", "POST"])
@auth.login_required
def admin_page():
    user = auth.current_user()
    if not auth.is_admin(user):
        return redirect(url_for("app_page"))
    if request.method == "POST":
        admin.remove_user(int(request.form.get("user_id", 0)), user["id"])
        return redirect(url_for("admin_page", q=request.args.get("q", "")))
    q = request.args.get("q", "")
    return render_template("admin.html", user=user, q=q, **admin.overview(q))


def start_background_model():
    ai.warm_up()
