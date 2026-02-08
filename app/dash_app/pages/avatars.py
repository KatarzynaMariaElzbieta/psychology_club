import os

from flask import abort, send_from_directory

ALLOWED_AVATARS = {"buchta.png", "rozmus.png", "kopec.png"}


def get_avatar_dir(app):
    """Ścieżka do folderu avatars w uploads"""
    return os.path.join(app.config["UPLOAD_FOLDER"], "avatars")


def register_avatar_routes(app):
    @app.route("/avatars/<filename>")
    def avatars(filename):
        avatar_dir = os.path.join(app.config["UPLOAD_FOLDER"], "avatars")
        return send_from_directory(avatar_dir, filename)
