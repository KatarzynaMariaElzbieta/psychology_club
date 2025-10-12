import dash
from dash import Output, Input, callback, html
import dash_mantine_components as dmc

from ..layout import menu_items
from ..layout import layout


layout = html.Div("artykuł")
dash.register_page(__name__, path='/artykuly', layout=layout)  # rejestracja strony



# @callback(
#     Output("navbar", "children"),
#     Output("navbar", "style"),
#     Input("burger", "opened"),
# )
# def toggle_mobile_menu(opened):
#     print(f"{opened=}")
#     if opened:
#         # Pionowe menu w navbarze na mobile
#         mobile_buttons = [dmc.Button(i, fullWidth=True) for i in menu_items]
#         return mobile_buttons, {"display": "block"}
#     return [], {"display": "none"}

