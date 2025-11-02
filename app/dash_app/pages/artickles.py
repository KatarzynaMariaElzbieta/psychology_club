import dash
from dash import Output, Input, callback, html
import dash_mantine_components as dmc

from .callendar import site_in_build

layout = site_in_build
dash.register_page(__name__, path='/artykuly', layout=layout)  # rejestracja strony
