import dash
import dash_mantine_components as dmc
from dash import html, dcc

logo_path = 'assets/images/logo-wam.png'

menu_items = {"Strona główna": "/aktualnosci/", "Artykuły": "/aktualnosci/artykuly",
              "Kalendarium": "/aktualnosci/kalendarium", "Projekty": "/aktualnosci/projekty"}

# Jeden komponent dla przycisków
menu_group = dmc.Group(
    [dmc.Anchor(k, href=v, visibleFrom="md") for k, v in menu_items.items()],
    id="menu-group",
    gap="sm"
)

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
                                    [dmc.MenuItem(i) for i in list(menu_items.keys()) + ["Logowanie/Rejestracja"]],
                                    hiddenFrom="md"),
                            ],

                        ),
                        align="center",
                    ),
                    dmc.Group(
                        [
                            menu_group,
                            dmc.Container(
                                html.A("Logowanie/Rejestracja", href='/login', className="mantine-Anchor-root"),
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
        html.Div([
            html.H1('Multi-page app with Dash Pages'),
            html.Div([
                html.Div(
                    dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
                ) for page in dash.page_registry.values()
            ]),
        ])
    ],
    header={
        "height": 70,  # 👈 Rezerwuje miejsce na header
    },
    footer={
        "height": 50,  # 👈 Rezerwuje miejsce na header
    },
)




