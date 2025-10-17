import dash
import dash_mantine_components as dmc
from dash import html, callback, Output, ALL, Input, callback_context, dcc
from flask_login import current_user

logo_path = 'assets/images/logo-wam.png'

menu_items = {"Strona główna": "/aktualnosci/", "Artykuły": "/aktualnosci/artykuly",
              "Kalendarium": "/aktualnosci/kalendarium", "Projekty": "/aktualnosci/projekty"}

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
            dash.page_container  # <-- tu ładują się strony
        ),
        dmc.AppShellFooter([
            dcc.Location(id="url"),
            dmc.Group(
                [
                    dmc.Anchor("O nas", href="/_todo", visibleFrom="md", style={"margin-bottom": "0.5rem"}),
                    dmc.Image(src=logo_path, w=130, fit="contain"),
                    dmc.Anchor("Kontakt", href="/_todo", visibleFrom="md", style={"margin-bottom": "0.5rem"}),
                ],
                justify="space-around",
                align="center"
            )
        ]),
    ],
    header={
        "height": 70,  # 👈 Rezerwuje miejsce na header
    },
    footer={
        "height": 50,  # 👈 Rezerwuje miejsce na header
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
        menu_items["Dodaj artykuł"] = "/aktualnosci/nowy_artykul"
        return (
            html.A("Wyloguj", href="/logout", className="mantine-Anchor-root"),
            [
                dmc.Anchor(k, href=v, visibleFrom="md") for k, v in menu_items.items()
            ],
                [dmc.MenuItem(k, href=v) for k, v in list(menu_items.items())]+
                [dmc.MenuItem(html.A("Wyloguj", href="/logout"))],

        )
    else:
        return (
            html.A("Logowanie", href="/login", className="mantine-Anchor-root"),
            [
                dmc.Anchor(k, href=v, visibleFrom="md") for k, v in menu_items.items()
            ],
                [dmc.MenuItem(k, href=v) for k, v in list(menu_items.items())] +
                [dmc.MenuItem(html.A("Logowanie", href="/login"))],
        )
