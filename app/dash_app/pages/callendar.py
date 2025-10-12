import dash
from dash import html



dash.register_page(__name__, path='/kalendarium')  # rejestracja strony
layout = html.Div("kalendarz")


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

