import dash_mantine_components as dmc
from dash import Dash
from dash_extensions.enrich import DashProxy

from .layout import layout


def init_dash(flask_app):
    dash_app = DashProxy(
        __name__,
        server=flask_app,
        url_base_pathname='/aktualnosci/',
        suppress_callback_exceptions=True,
        use_pages=True,
    )
    dash_app.title = "Studenckie Koło Psychologii WAM"
    dash_app.layout = dmc.MantineProvider(layout)
    return dash_app
