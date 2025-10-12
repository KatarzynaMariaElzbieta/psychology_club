import dash
from dash import html

dash.register_page(__name__, path='/projekty/')  # rejestracja strony
layout = html.Div("projekty")


