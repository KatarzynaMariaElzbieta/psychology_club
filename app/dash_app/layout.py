import dash
import dash_mantine_components as dmc
from dash import html, dcc
from flask import url_for

# layout = dmc.AppShell(
#     [
#         dmc.AppShellHeader(
#             dmc.Group(
#                 [
#                     dmc.Burger(
#                         id="burger",
#                         size="sm",
#                         hiddenFrom="sm",
#                         opened=False,
#                     ),
#                     dmc.Title("Studenckie Koło Psychologii WAM", c="blue"),
#                 ],
#                 h="100%",
#                 px="md",
#             )
#         ),
# dmc.AppShellNavbar("Pasek nawigacyjny"),
# dmc.AppShellAside("Panel boczny"),
# dmc.AppShellMain("Treść główna"),
# dmc.AppShellFooter("Stopka")
# ],
# padding = "md",
# )

logo_path = 'assets/images/logo-wam.png'


menu_buttons = [dmc.Button(i, fullWidth=True) for i in ["Strona główna", "Artykuły", "Kalendarium", "Projekty"]]

menu_items = ["Strona główna", "Artykuły", "Kalendarium", "Projekty"]

# Jeden komponent dla przycisków
menu_group = dmc.Group(
    [dmc.Button(i, visibleFrom="md") for i in menu_items],
    id="menu-group",
    gap="sm"
)


def generate_card(number):
    return dmc.CarouselSlide(dmc.Card(
        [
            dmc.CardSection(dmc.Text(number)),
            dmc.CardSection(dmc.Image(
                src="https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-4.png"
            )
            ),
            dmc.CardSection(dmc.Text("jakiś opis tego co się dzieje bla bla bla"))
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        # w=350,
    ))


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
                                dmc.MenuDropdown([dmc.MenuItem(i) for i in menu_items + ["Logowanie/Rejestracja"]],
                                                 hiddenFrom="md"),
                            ],

                        ),
                        align="center",
                    ),
                    dmc.Group(
                        [
                            menu_group,
                            dmc.Button("Logowanie/Rejestracja", visibleFrom="md")
                        ],
                        px="md",
                        align="start",
                        justify="space-between",
                        style={"width": "100%", "hight": "100%", "padding-bottom": "1rem"}
                    )
                ],
                    justify="center",
                    align="center",
                    h=70,
                ),
            ]),
        dmc.AppShellMain(
            dmc.Center([
            dmc.Carousel(
                [
                    generate_card(i) for i in range(1, 5)
                ],
                id="carousel-simple",
                orientation="horizontal",
                withControls=True,
                withIndicators=True,
                slideSize="33.3333%",
                slideGap="md",
                emblaOptions={"loop": True, "align": "start", "slidesToScroll": 1},
                style={"margin": "1rem"}
            )
]),

        ),
        dmc.AppShellFooter([
            dmc.Group(
                [
                    dmc.Text("O nas"),
                    dmc.Image(src=logo_path, w=130, fit="contain"),
                    dmc.Text("A tu coś innegp"),
                ],
                justify="space-between",
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
            dash.page_container
        ])
    ],
    header={
        "height": 70,  # 👈 Rezerwuje miejsce na header
    },
    footer={
        "height": 50,  # 👈 Rezerwuje miejsce na header
    },
)
