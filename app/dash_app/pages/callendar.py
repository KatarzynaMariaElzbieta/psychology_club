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
