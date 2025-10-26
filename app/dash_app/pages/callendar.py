import dash
from dash import html
import dash_mantine_components as dmc

dash.register_page(__name__, path='/kalendarium')  # rejestracja strony

def site_in_build():
    return dmc.Center(
        [
            dmc.Paper(
                "Stona w budowie.",
                radius="sm",
                p="lg",
                shadow="sm",
                withBorder=False,
                # other props...
            )
        ],
    )

layout = site_in_build
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
