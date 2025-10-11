import dash
from dash import Output, Input, callback, State
import dash_mantine_components as dmc

from ..layout import menu_items
from ..layout import layout


dash.register_page(__name__, path='/aktualnosci')  # rejestracja strony
layout = layout


@callback(
    Output("navbar", "children"),
    Output("navbar", "style"),
    Input("burger", "opened"),
    State("navbar", "style"),
)
def toggle_mobile_menu(opened, style):
    print(f"{opened=}")
    style = style if style else {}
    if opened:
        # Pionowe menu w navbarze na mobile
        mobile_buttons = [dmc.Button(i, fullWidth=True) for i in menu_items]
        style["display"] = "block"
        return mobile_buttons, style
    style["display"] = "none"
    return [], style

