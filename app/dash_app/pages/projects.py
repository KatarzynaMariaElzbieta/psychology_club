import dash
import dash_mantine_components as dmc
from dash import Input, Output, callback, html

from app.models import Project

dash.register_page(
    __name__,
    path="/projekty",
    name="Projekty",
    title="Projekty | Psychowam",
    description="Projekty i inicjatywy realizowane przez Koło Psychologii WAM.",
)  # rejestracja strony
layout = dmc.Stack(
    [
        dmc.Container(
            [
                dmc.Title("Projekty"),
                dmc.Divider(variant="solid", w="100%"),
            ],
        ),
        dmc.Stack(
            [
                html.Div(
                    "Znajdziesz tu aktualnie prowadzone przez koło projekty, "
                    "w które możesz się zaangażować będąc naszym członkiem lub sympatykiem, "
                ),
            ],
            align="center",
            gap="xs",
        ),
        dmc.Box(id="projects_containter"),
    ],
    align="center",
    justify="center",
    gap="md",
    m={
        "base": "5% 15%",
        "md": "3% 25%",
    },
    # style={"min-height": "calc(100vh - 130px)"},
)


def project_card(project: Project):
    responsible_name = project.responsible.username or project.responsible.email
    return dmc.Paper(
        dmc.Stack(
            [
                dmc.Group(
                    [
                        dmc.Title(project.title, order=4),
                        dmc.Badge(project.project_type, variant="light"),
                    ],
                    justify="space-between",
                    align="center",
                    wrap="wrap",
                ),
                dmc.Text(project.description, size="sm"),
                dmc.Text(f"Koordynator projektu: {responsible_name}", size="xs", fw=600),
                dmc.Anchor(
                    "Zobacz szczegóły",
                    href=f"/projekty/{project.id}",
                    style={"color": "Blue"},
                ),
            ],
            gap="xs",
        ),
        radius="lg",
        p="lg",
        shadow="md",
        withBorder=True,
        w="100%",
    )


@callback(
    Output("projects_containter", "children"),
    Input("projects_containter", "id"),
)
def load_projects(_):
    projects = Project.query.filter_by(is_active=True).order_by(Project.created_at.asc()).all()
    if not projects:
        return dmc.Text("Brak projektów do wyświetlenia.")

    return dmc.SimpleGrid(
        [project_card(project) for project in projects],
        cols={"base": 1, "md": 2},
        spacing="lg",
        verticalSpacing="lg",
    )
