import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from flask_login import current_user

from app import db
from app.dash_app.src import require_roles
from app.models import Project, User

dash.register_page(__name__, path_template="/edytuj_projekt/<id>")

DEFAULT_WHERE_FOR_HELP_TABLE_HTML = """
<table>
  <thead>
    <tr>
      <th>Instytucja</th>
      <th>Zakres pomocy</th>
      <th>Kontakt</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Poradnia A</td>
      <td>Konsultacje psychologiczne</td>
      <td>email@poradniaa.pl</td>
    </tr>
    <tr>
      <td>Fundacja B</td>
      <td>Wsparcie kryzysowe</td>
      <td>+48 123 456 789</td>
    </tr>
  </tbody>
</table>
"""


base_layout = html.Div(
    [
        dmc.Container(
            [
                dmc.TextInput(
                    label="Tytuł projektu",
                    placeholder="Wpisz tytuł",
                    id="project-title-input-edit",
                    required=True,
                ),
                dmc.TextInput(
                    label="Typ projektu",
                    placeholder="Np. badawczy, edukacyjny, społeczny",
                    id="project-type-input-edit",
                    required=True,
                ),
                dmc.Textarea(
                    label="Opis projektu",
                    placeholder="Krótki opis projektu (do 600 znaków)",
                    id="project-description-input-edit",
                    autosize=True,
                    minRows=3,
                    required=True,
                    mb=20,
                ),
                dmc.RichTextEditor(
                    id="project-extra-content-input-edit",
                    html="",
                    mih=300,
                    mb=20,
                    toolbar={
                        "sticky": True,
                        "controlsGroups": [
                            [
                                {
                                    "CustomControl": {
                                        "ariaLabel": "Wstaw tabelę",
                                        "title": "Wstaw tabelę",
                                        "children": [
                                            DashIconify(
                                                icon="mdi:table-plus",
                                                width=18,
                                                height=18,
                                            )
                                        ],
                                        "onClick": {
                                            "function": "rteInsertTable",
                                            "options": {
                                                "table": {
                                                    "rows": 3,
                                                    "cols": 3,
                                                    "withHeaderRow": True,
                                                }
                                            },
                                        },
                                    }
                                },
                                {
                                    "CustomControl": {
                                        "ariaLabel": "Dodaj wiersz powyżej",
                                        "title": "Dodaj wiersz powyżej",
                                        "children": [
                                            DashIconify(
                                                icon="mdi:table-row-plus-before",
                                                width=18,
                                                height=18,
                                            )
                                        ],
                                        "onClick": {"function": "rteAddRowBefore"},
                                    }
                                },
                                {
                                    "CustomControl": {
                                        "ariaLabel": "Dodaj wiersz poniżej",
                                        "title": "Dodaj wiersz poniżej",
                                        "children": [
                                            DashIconify(
                                                icon="mdi:table-row-plus-after",
                                                width=18,
                                                height=18,
                                            )
                                        ],
                                        "onClick": {"function": "rteAddRowAfter"},
                                    }
                                },
                                {
                                    "CustomControl": {
                                        "ariaLabel": "Usuń wiersz",
                                        "title": "Usuń wiersz",
                                        "children": [
                                            DashIconify(
                                                icon="mdi:table-row-remove",
                                                width=18,
                                                height=18,
                                            )
                                        ],
                                        "onClick": {"function": "rteDeleteRow"},
                                    }
                                },
                                {
                                    "CustomControl": {
                                        "ariaLabel": "Dodaj kolumnę po lewej",
                                        "title": "Dodaj kolumnę po lewej",
                                        "children": [
                                            DashIconify(
                                                icon="mdi:table-column-plus-before",
                                                width=18,
                                                height=18,
                                            )
                                        ],
                                        "onClick": {"function": "rteAddColumnBefore"},
                                    }
                                },
                                {
                                    "CustomControl": {
                                        "ariaLabel": "Dodaj kolumnę po prawej",
                                        "title": "Dodaj kolumnę po prawej",
                                        "children": [
                                            DashIconify(
                                                icon="mdi:table-column-plus-after",
                                                width=18,
                                                height=18,
                                            )
                                        ],
                                        "onClick": {"function": "rteAddColumnAfter"},
                                    }
                                },
                                {
                                    "CustomControl": {
                                        "ariaLabel": "Usuń kolumnę",
                                        "title": "Usuń kolumnę",
                                        "children": [
                                            DashIconify(
                                                icon="mdi:table-column-remove",
                                                width=18,
                                                height=18,
                                            )
                                        ],
                                        "onClick": {"function": "rteDeleteColumn"},
                                    }
                                },
                                {
                                    "CustomControl": {
                                        "ariaLabel": "Usuń tabelę",
                                        "title": "Usuń tabelę",
                                        "children": [
                                            DashIconify(
                                                icon="mdi:table-remove",
                                                width=18,
                                                height=18,
                                            )
                                        ],
                                        "onClick": {"function": "rteDeleteTable"},
                                    }
                                },
                            ],
                            ["Bold", "Italic", "Underline", "Code"],
                            ["H1", "H2", "H3", "H4", "H5", "H6"],
                            ["Hr", "Strikethrough", "ClearFormatting", "Blockquote"],
                            ["BulletList", "OrderedList"],
                            ["Link", "Unlink"],
                            ["AlignLeft", "AlignCenter", "AlignJustify", "AlignRight"],
                            ["SourceCode"],
                            ["Undo", "Redo"],
                        ],
                    },
                ),
                dmc.Select(
                    label="Osoba odpowiedzialna",
                    placeholder="Wybierz osobę",
                    id="project-responsible-input-edit",
                    data=[],
                    searchable=True,
                    clearable=False,
                    mb=20,
                ),
                dmc.Switch(
                    label="Projekt aktywny",
                    id="project-active-input-edit",
                    checked=True,
                    mb=20,
                ),
                dmc.Button("💾 Zapisz zmiany", id="save-project-btn-edit", color="teal"),
                dcc.Store(id="project-id-store-edit", data=""),
            ],
            size="lg",
            p="xl",
        )
    ],
    id="edit-project-content",
    style={"display": "none"},
)


@require_roles("zarządzanie projektami")
def serve_layout(id=None, **_kwargs):
    return base_layout


layout = serve_layout


@callback(
    Output("project-title-input-edit", "value"),
    Output("project-type-input-edit", "value"),
    Output("project-description-input-edit", "value"),
    Output("project-extra-content-input-edit", "html"),
    Output("project-responsible-input-edit", "data"),
    Output("project-responsible-input-edit", "value"),
    Output("project-active-input-edit", "checked"),
    Output("project-id-store-edit", "data"),
    Output("edit-project-content", "style"),
    Input("url", "pathname"),
    prevent_initial_call="initial_duplicate",
)
def load_project_for_edit(pathname):
    try:
        project_id = int(pathname.rstrip("/").split("/")[-1])
    except (ValueError, AttributeError, IndexError):
        raise PreventUpdate

    project = Project.query.get(project_id)
    if not project:
        raise PreventUpdate

    users = User.query.order_by(User.username.asc().nullslast(), User.email.asc()).all()
    responsible_options = [{"value": str(user.id), "label": user.username or user.email} for user in users]

    extra_content = project.extra_content or ""
    if project.id == 1 and not extra_content:
        extra_content = DEFAULT_WHERE_FOR_HELP_TABLE_HTML

    return (
        project.title,
        project.project_type,
        project.description,
        extra_content,
        responsible_options,
        str(project.responsible_id),
        bool(project.is_active),
        project.id,
        {"display": "block"},
    )


@callback(
    Output("save-project-btn-edit", "children"),
    Input("save-project-btn-edit", "n_clicks"),
    State("project-title-input-edit", "value"),
    State("project-type-input-edit", "value"),
    State("project-description-input-edit", "value"),
    State("project-extra-content-input-edit", "html"),
    State("project-responsible-input-edit", "value"),
    State("project-active-input-edit", "checked"),
    State("project-id-store-edit", "data"),
    prevent_initial_call=True,
)
def save_project(
    n_clicks,
    title,
    project_type,
    description,
    extra_content,
    responsible_id,
    is_active,
    project_id,
):
    if not getattr(current_user, "is_authenticated", False) or not current_user.has_role("zarządzanie projektami"):
        return "⛔ Brak uprawnień"

    if not title or not project_type or not description:
        return "⚠️ Uzupełnij wszystkie pola!"

    try:
        responsible_id = int(responsible_id)
    except (TypeError, ValueError):
        return "⚠️ Wybierz osobę odpowiedzialną!"

    project = Project.query.get(project_id)
    if not project:
        return "⚠️ Nie znaleziono projektu!"

    project.title = title.strip()
    project.project_type = project_type.strip()
    project.description = description.strip()
    project.extra_content = extra_content or ""
    project.responsible_id = responsible_id
    project.is_active = bool(is_active)
    db.session.commit()

    return "✅ Zapisano zmiany!"
