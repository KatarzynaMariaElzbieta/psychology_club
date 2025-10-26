import dash
from dash import html

from app.dash_app.pages.callendar import site_in_build


dash.register_page(__name__, path='/o-nas/')  # rejestracja strony
layout = site_in_build


