from dash import Dash
from flask import url_for
from .layout import layout


def init_dash(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/aktualnosci/',
        suppress_callback_exceptions=True,
    )
    dash_app.title = "Studenckie Koło Psychologii WAM"
    dash_app.layout = layout
    return dash_app
