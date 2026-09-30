"""Download generated files (only the owner can fetch them)."""
from flask import Blueprint, abort, send_from_directory, session

from backend.auth import login_required
from backend.config import GENERATED_DIR

bp = Blueprint("downloads", __name__)


@bp.route("/download/<path:name>")
@login_required
def download(name):
    if not name.startswith(f"u{session['user_id']}_"):
        abort(404)
    return send_from_directory(GENERATED_DIR, name, as_attachment=True)
