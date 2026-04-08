import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, callback
from flask_login import current_user

from app import db
from app.dash_app.src import require_roles
from app.models import Project, User

dash.register_page(__name__, path="/nowy_projekt", name="Nowy projekt")


@require_roles("zarządzanie projektami")
def serve_layout():
    users = User.query.order_by(User.username.asc().nullslast(), User.email.asc()).all()
    responsible_options = [{"value": str(user.id), "label": user.username or user.email} for user in users]
    current_user_id = str(current_user.id) if current_user.is_authenticated else None
    return dmc.Container(
        [
            dmc.TextInput(
                label="Tytuł projektu",
                placeholder="Wpisz tytuł",
                id="project-title-input",
                required=True,
            ),
            dmc.TextInput(
                label="Typ projektu",
                placeholder="Np. badawczy, edukacyjny, społeczny",
                id="project-type-input",
                required=True,
            ),
            dmc.Textarea(
                label="Opis projektu",
                placeholder="Krótki opis projektu (do 600 znaków)",
                id="project-description-input",
                autosize=True,
                minRows=3,
                required=True,
                mb=20,
            ),
            dmc.RichTextEditor(
                id="project-extra-content-input",
                html="",
                mih=300,
                mb=20,
                toolbar={
                    "sticky": True,
                    "controlsGroups": [
                        ["Bold", "Italic", "Underline", "Code"],
                        ["H1", "H2", "H3", "H4", "H5", "H6"],
                        ["Strikethrough", "ClearFormatting", "Blockquote"],
                        ["BulletList", "OrderedList"],
                        ["Link", "Unlink"],
                        ["AlignLeft", "AlignCenter", "AlignJustify", "AlignRight"],
                        ["Undo", "Redo"],
                    ],
                },
            ),
            dmc.Select(
                label="Osoba odpowiedzialna",
                placeholder="Wybierz osobę",
                id="project-responsible-input",
                data=responsible_options,
                value=current_user_id,
                searchable=True,
                clearable=False,
                mb=20,
            ),
            dmc.Button("💾 Zapisz projekt", id="save-project-btn", color="teal"),
        ],
        size="lg",
        p="xl",
    )


layout = serve_layout


@callback(
    Output("save-project-btn", "children"),
    Input("save-project-btn", "n_clicks"),
    State("project-title-input", "value"),
    State("project-type-input", "value"),
    State("project-description-input", "value"),
    State("project-extra-content-input", "html"),
    State("project-responsible-input", "value"),
    prevent_initial_call=True,
)
def save_project(n_clicks, title, project_type, description, extra_content, responsible_id):
    if not getattr(current_user, "is_authenticated", False) or not current_user.has_role("zarządzanie projektami"):
        return "⛔ Brak uprawnień"

    if not title or not project_type or not description:
        return "⚠️ Uzupełnij wszystkie pola!"

    try:
        responsible_id = int(responsible_id)
    except (TypeError, ValueError):
        return "⚠️ Wybierz osobę odpowiedzialną!"

    responsible_user = User.query.get(responsible_id)
    if not responsible_user:
        return "⚠️ Nie znaleziono osoby odpowiedzialnej!"

    project = Project(
        title=title.strip(),
        project_type=project_type.strip(),
        description=description.strip(),
        extra_content=extra_content or "",
        responsible=responsible_user,
    )
    db.session.add(project)
    db.session.commit()

    return "✅ Projekt zapisany!"
