import uuid
from datetime import datetime
from flask_security import UserMixin, RoleMixin
from .extensions import db

# --- Tabele asocjacyjne ---

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

authors_articles = db.Table(
    'authors_articles',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('article_id', db.Integer(), db.ForeignKey('article.id'))
)

articles_tags = db.Table(
    'articles_tags',
    db.Column('tag_id', db.Integer(), db.ForeignKey('tag.id')),
    db.Column('article_id', db.Integer(), db.ForeignKey('article.id'))
)

# --- Modele główne ---

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime(), default=datetime.utcnow)

    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    roles = db.relationship('Role', secondary=roles_users, backref='users')

    def __repr__(self):
        return f"{self.email}"


class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<Tag {self.name}>"


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # short_content = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacje
    authors = db.relationship('User', secondary=authors_articles, backref='articles')
    tags = db.relationship('Tag', secondary=articles_tags, backref='articles')
    images = db.relationship('Image', backref='article', cascade="all, delete-orphan")

    @property
    def main_image(self):
        """Zwraca główny obrazek (lub None, jeśli nie ustawiono)."""
        return next((img for img in self.images if img.is_main), None)

    def __repr__(self):
        return f"<Article {self.title}>"


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    is_main = db.Column(db.Boolean, default=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)

    def __repr__(self):
        flag = " (MAIN)" if self.is_main else ""
        return f"<Image {self.file_path}{flag}>"