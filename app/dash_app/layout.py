import dash
import dash_mantine_components as dmc
from dash import html, callback, Output, ALL, Input, callback_context, dcc
from flask_login import current_user
from flask import current_app, url_for

logo2_path = '/static/local/logo-wam.png'
logo_path = '/static/local/LOGO.svg'


def return_logo_path(path):
    return url_for("dash_app", filename=path)


menu_items = {"Strona główna": "/", "Artykuły": "/artykuly",
              "Kalendarium": "/kalendarium", "Projekty": "/projekty"}

# Jeden komponent dla przycisków

dmc.Anchor(
    "Underline on hover",
    href="https://www.dash-mantine-components.com/",
    target="_blank",
    underline="hover",
),

layout = dmc.AppShell(
    children=[
        dmc.AppShellHeader(
            [
                dmc.Group([

                    dmc.Group(
                        dmc.Menu(
                            [
                                dmc.MenuTarget(dmc.Burger(id="burger",
                                                          hiddenFrom="md",
                                                          size="sm",
                                                          color="white",
                                                          style={"padding-top": "1rem"})),
                                dmc.MenuDropdown(
                                    [],
                                    id="menu_burger",
                                    hiddenFrom="md"),
                            ],

                        ),
                        align="center",
                    ),
                    dmc.Group(
                        [
                            dmc.Group(id="menu_items", gap="sm"),
                            dmc.Container(
                                id="login_logout_desktop",
                                visibleFrom="md",
                                m=0
                            )
                        ],
                        px="md",
                        align="start",
                        justify="space-between",
                        style={"width": "100%", "hight": "100%", "padding-bottom": "1.3rem"}
                    )
                ],
                    justify="center",
                    align="center",
                    h=70,
                ),
            ]),
        dmc.AppShellMain(
            [
                dmc.Affix(dmc.Image(src=logo2_path, w=150),
                          position={"top": "70", "right": "lg"}
                          ),
                dash.page_container  # <-- tu ładują się strony

            ],
        ),
        dmc.AppShellFooter([
            dcc.Location(id="url"),
            dmc.Group(
                [
                    dmc.Anchor("O nas", href="/o-nas", visibleFrom="md", style={"margin-bottom": "0.5rem"}),\
                    dmc.Affix(dmc.Image(src=logo_path, w=100, fit="contain",
                                        style={"border": "solid", "color": "#1f2e4f"}
                              ), position={"bottom": "-10", "right": "50%"}),
                    dmc.Anchor("Kontakt", href="/kontakt", visibleFrom="md", style={"margin-bottom": "0.5rem"}),
                ],
                h="100%",
                justify="space-around",
                align="center"
            )
        ],
        # style={"position": "relative"}
        ),
    ],
    header={
        "height": 70,  # 👈 Rezerwuje miejsce na header
    },
    footer={
        "height": 60,  # 👈 Rezerwuje miejsce na footer
    },
)


@callback(
    Output("login_logout_desktop", "children"),
    Output("menu_items", "children"),
    Output("menu_burger", "children"),
    Input("url", "pathname"),
)
def login_logout(_):
    if current_user and current_user.is_authenticated:
        menu_items["Dodaj artykuł"] = "/nowy_artykul"
        return (
            html.A("Wyloguj", href="/auth/logout", className="mantine-Anchor-root"),
            [
                dmc.Anchor(k, href=v, visibleFrom="md") for k, v in menu_items.items()
            ],
            [dmc.MenuItem(k, href=v) for k, v in list(menu_items.items())] +
            [dmc.MenuItem(html.A("Wyloguj", href="/auth/logout"))],

        )
    else:
        if "Dodaj artykuł" in menu_items.keys():
            menu_items.pop("Dodaj artykuł")
        return (
            html.A("Logowanie", href="/auth/login", className="mantine-Anchor-root"),
            [
                dmc.Anchor(k, href=v, visibleFrom="md") for k, v in menu_items.items()
            ],
            [dmc.MenuItem(k, href=v) for k, v in list(menu_items.items())] +
            [dmc.MenuItem(html.A("Logowanie", href="/auth/login"))],
        )
