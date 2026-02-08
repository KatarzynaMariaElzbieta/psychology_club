import dash
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify


dash.register_page(__name__, path="/kontakt/", name="Kontakt")  # rejestracja strony
layout = dmc.Stack(
    [
        dmc.Container(
            [
                dmc.Title("Kontakt"),
                dmc.Divider(variant="solid", w="100%"),
            ]
        ),
        dmc.Stack(
            [
                html.Div("Masz pytania dotyczące działalności koła?"),
                html.Div("Chcesz do nas dołączyć?"),
                html.Div("Napisz do nas."),
            ],
            align="center",
            gap="xs",
        ),
        dmc.Grid(
            [
                dmc.GridCol(
                    dmc.Paper(
                        [
                            dmc.Group(
                                [
                                    dmc.ThemeIcon(
                                        DashIconify(icon="system-uicons:mail", width=35),
                                        variant="light",
                                        size="xl",
                                        radius="xl",
                                    ),
                                    dmc.Title("Kontakt ogólny", order=3),
                                ],
                                className="card_title",
                            ),
                            dmc.Divider(
                                variant="solid",
                                w="100%",
                            ),
                            dmc.Text("Najlepszy sposób kontaktu w sprawach ogólnych, współprac i wydarzeń:", p=10),
                            dmc.CopyButton("kontakt@psychowam.pl", variant="light", fullWidth="true"),
                        ],
                        radius="md",
                        p="lg",
                        shadow="xs",
                        withBorder=True,
                        h="100%",
                    ),
                    span={"base": 12, "md": 10, "lg": 5},
                ),
                dmc.GridCol(
                    dmc.Paper(
                        [
                            dmc.Group(
                                [
                                    dmc.ThemeIcon(
                                        DashIconify(icon="stash:share", width=32),
                                        variant="light",
                                        size="xl",
                                        radius="xl",
                                    ),
                                    dmc.Title("Media społecznościowe", order=3),
                                ],
                                wrap="nowrap",
                                className="card_title",
                            ),
                            dmc.Divider(
                                variant="solid",
                                w="100%",
                            ),
                            dmc.Group(
                                [
                                    DashIconify(icon="skill-icons:instagram"),
                                    dmc.Box(
                                        [
                                            dmc.Title("Instagram", order=5),
                                            dmc.Anchor(
                                                "kolopsychologicznewam",
                                                href="https://www.instagram.com/kolopsychologicznewam/",
                                                target="_blank",
                                                underline="always",
                                                style={"color": "blue"},
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            dmc.Divider(
                                variant="solid",
                                w="100%",
                            ),
                            dmc.Group(
                                [
                                    DashIconify(icon="logos:facebook"),
                                    dmc.Box(
                                        [
                                            dmc.Title("Grupa na FB", order=5),
                                            dmc.Anchor(
                                                "Koło psychologiczne WAM",
                                                href="https://www.facebook.com/groups/161959010100196",
                                                target="_blank",
                                                underline="always",
                                                style={"color": "blue"},
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                        ],
                        radius="md",
                        p="lg",
                        shadow="xs",
                        withBorder=True,
                    ),
                    span={"base": 12, "md": 10, "lg": 5},
                ),
                dmc.GridCol(
                    dmc.Paper(
                        [
                            dmc.Group(
                                [
                                    dmc.ThemeIcon(
                                        DashIconify(icon="fluent:people-team-28-regular", width=32),
                                        variant="light",
                                        size="xl",
                                        radius="xl",
                                    ),
                                    dmc.Title("Zarząd koła", order=3),
                                ],
                                className="card_title",
                            ),
                            dmc.Divider(
                                variant="solid",
                                w="100%",
                            ),
                            dmc.Group(
                                [
                                    dmc.Avatar(src="/avatars/buchta.png"),
                                    dmc.Box(
                                        [
                                            dmc.Title("Przewodniczący: Michał Buchta", order=6),
                                            dmc.Text("m.buchta@psychowam.pl"),
                                        ]
                                    ),
                                ]
                            ),
                            dmc.Divider(
                                variant="solid",
                                w="100%",
                            ),
                            dmc.Group(
                                [
                                    dmc.Avatar(src=f"/avatars/rozmus.png"),
                                    dmc.Box(
                                        [
                                            dmc.Title("Zastępczyni: Aleksandra Rozmus", order=6),
                                            dmc.Text("a.rozmus@psychowam.pl"),
                                        ]
                                    ),
                                ]
                            ),
                            dmc.Divider(
                                variant="solid",
                                w="100%",
                            ),
                            dmc.Group(
                                [
                                    dmc.Avatar(src="/avatars/kopec.png"),
                                    dmc.Box(
                                        [
                                            dmc.Title("Sekretarz: Katarzyna Kopeć", order=6),
                                            dmc.Text("k.kopec@psychowam.pl"),
                                        ]
                                    ),
                                ]
                            ),
                        ],
                        radius="md",
                        p="lg",
                        shadow="xs",
                        withBorder=True,
                    ),
                    span={"base": 12, "md": 10},
                ),
            ],
            align="stretch",
            justify="center",
        ),
    ],
    align="center",
    justify="center",
    gap="md",
    m={"base": "5% 25%", "md": "0 25%"},
    style={"min-height": "calc(100vh - 130px)"},
)
