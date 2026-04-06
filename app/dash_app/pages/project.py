import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, html
from dash_extensions import Purify
from flask_login import current_user

from app import db
from app.dash_app.src import prepare_html
from app.models import Project

dash.register_page(__name__, path_template="/projekty/<id>")
_CURRENT_MODULE = __name__


layout = html.Div(id="project-content")


@callback(
    Output("project-content", "children"),
    Input("url", "pathname"),
)
def show_project(pathname):
    if not pathname:
        return dmc.Text("Nieprawidłowy adres projektu")

    normalized_path = pathname.rstrip("/") or "/"
    for page in dash.page_registry.values():
        if page.get("module") == _CURRENT_MODULE:
            continue
        page_path = (page.get("path") or "").rstrip("/") or "/"
        if page_path == normalized_path:
            layout_obj = page.get("layout")
            return layout_obj() if callable(layout_obj) else layout_obj

    try:
        project_id = int(normalized_path.split("/")[-1])
    except (ValueError, AttributeError, IndexError):
        return dmc.Text("Nieprawidłowy adres projektu")

    project = db.session.get(Project, project_id)
    if not project:
        return dmc.Text("Nie znaleziono projektu")

    safe_html = prepare_html(project.extra_content or "")
    custom_html = prepare_html(project.custom_page_html or "")
    can_manage = getattr(current_user, "is_authenticated", False) and current_user.has_role("zarządzanie projektami")
    status_label = "Aktywny" if project.is_active else "Nieaktywny"
    status_color = "green" if project.is_active else "red"
    manage_display = "inline-flex" if can_manage else "none"
    edit_display = "inline" if can_manage else "none"
    if project.custom_page_enabled and custom_html:
        return dmc.Container(
            [
                dmc.Group(
                    [
                        dmc.Badge(status_label, color=status_color, variant="filled", id="project-status-badge"),
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
                    mb="md",
                    style={"display": manage_display},
                ),
                html.Div([Purify(html=custom_html)]),
                dcc.Store(id="project-id-store", data=project.id),
            ],
            size="lg",
            mt=20,
            mb=20,
        )

    return dmc.Container(
        dmc.Paper(
            [
                dmc.Title(project.title, order=1, style={"marginBottom": "1rem", "padding-top": "1rem"}),
                dmc.Group(
                    [
                        dmc.Badge(project.project_type, variant="light"),
                        dmc.Badge(status_label, color=status_color, variant="filled", id="project-status-badge"),
                        dmc.Text(
                            f"Odpowiedzialna osoba: {project.responsible.username or project.responsible.email}",
                            size="sm",
                            fw=600,
                        ),
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
                html.Hr(),
                html.Div([Purify(html=safe_html)]) if safe_html else None,
                dcc.Store(id="project-id-store", data=project.id),
            ],
            radius="lg",
            p="3rem",
            shadow="md",
            withBorder=True,
        ),
        size="md",
        mt=20,
        mb=20,
    )


@callback(
    Output("project-toggle-btn", "children"),
    Output("project-toggle-btn", "color"),
    Output("project-status-badge", "children"),
    Output("project-status-badge", "color"),
    Input("project-toggle-btn", "n_clicks"),
    State("project-id-store", "data"),
    prevent_initial_call=True,
)
def toggle_project_status(n_clicks, project_id):
    if not getattr(current_user, "is_authenticated", False) or not current_user.has_role("zarządzanie projektami"):
        return "⛔ Brak uprawnień", "gray", "Nieznany", "gray"

    project = db.session.get(Project, project_id)
    if not project:
        return "⚠️ Nie znaleziono projektu", "gray", "Nieznany", "gray"

    project.is_active = not project.is_active
    db.session.commit()

    status_label = "Aktywny" if project.is_active else "Nieaktywny"
    status_color = "green" if project.is_active else "red"
    button_label = "Dezaktywuj projekt" if project.is_active else "Aktywuj projekt"
    button_color = "red" if project.is_active else "green"
    return button_label, button_color, status_label, status_color
