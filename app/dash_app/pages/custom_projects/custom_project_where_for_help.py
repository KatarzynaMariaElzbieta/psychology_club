import dash
import dash_mantine_components as dmc
from dash import html
from dash_extensions import Purify
from flask_login import current_user

from app import db
from app.dash_app.src import prepare_html
from app.models import Project

dash.register_page(__name__, path="/projekty/1", name="Gdzie po pomoc?")  # rejestracja strony

DEFAULT_TABLE_HTML = ""


def create_layout_custom():
    project = db.session.get(Project, 1)
    can_manage = getattr(current_user, "is_authenticated", False) and current_user.has_role("zarządzanie projektami")
    manage_display = "inline-flex" if can_manage else "none"
    edit_display = "inline" if can_manage else "none"
    table_html = project.extra_content or DEFAULT_TABLE_HTML
    safe_html = prepare_html(table_html)

    return dmc.Center(
        [
            dmc.Paper(
                [
                    dmc.Stack(
                        [
                            dmc.Title("Gdzie po pomoc?"),
                            dmc.Text(
                                f"Koordynator projektu: {project.responsible.username or project.responsible.email}",
                                size="sm",
                                fw=600,
                            ),
                            dmc.Badge(project.project_type, variant="light"),
                            dmc.Group(
                                [
                                    dmc.Anchor(
                                        "Edytuj projekt",
                                        href=f"/edytuj_projekt/{project.id}",
                                        style={"color": "Blue", "display": edit_display},
                                    ),
                                    dmc.Button(
                                        "Dezaktywuj projekt" if project.is_active else "Aktywuj projekt",
                                        id="project-toggle-btn",
                                        color="red" if project.is_active else "green",
                                        variant="light",
                                        size="xs",
                                        style={"display": manage_display},
                                    ),
                                ],
                                gap="sm",
                            ),
                            dmc.Text(project.description, mt="md"),
                        ],
                        align="center",
                    ),
                    dmc.Divider(),
                    html.Div(
                        [Purify(html=safe_html)],
                        className="where-for-help-content",
                    )
                    if safe_html
                    else None,
                ],
                radius="lg",
                p="3rem",
                shadow="md",
                withBorder=True,
                w={"base": "90vw", "md": "70vw"},
                style={"margin": "2rem"},
            )
        ]
    )


layout = create_layout_custom
