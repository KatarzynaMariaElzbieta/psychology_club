import os

from flask import abort, send_from_directory

# Lista awatarów, które chcesz udostępniać
ALLOWED_AVATARS = {"buchta.png", "rozmus.png", "kopec.png"}


def get_avatar_dir(app):
    """Ścieżka do folderu avatars w uploads"""
    return os.path.join(app.config["UPLOAD_FOLDER"], "avatars")


def register_avatar_routes(app):
    """Rejestruje route /avatars/<filename>"""

    @app.route("/avatars/<filename>")
    def serve_avatar(filename):
        if filename not in ALLOWED_AVATARS:
            abort(404)
        return send_from_directory(get_avatar_dir(app), filename)
