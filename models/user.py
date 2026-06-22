"""User model and authentication helpers."""

from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    """Application users who can upload, like, comment and report artwork."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)
    bio = db.Column(db.Text, default="")
    profile_image = db.Column(db.String(255), default="", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    artworks = db.relationship("Artwork", back_populates="author", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    likes = db.relationship("Like", back_populates="user", cascade="all, delete-orphan")
    shares = db.relationship("Share", back_populates="user", cascade="all, delete-orphan")
    favourites = db.relationship("Favourite", back_populates="user", cascade="all, delete-orphan")
    lessons = db.relationship("Lesson", back_populates="author", cascade="all, delete-orphan")
    lesson_progress = db.relationship("LessonProgress", back_populates="user", cascade="all, delete-orphan")
    reports = db.relationship(
        "Report",
        back_populates="reporter",
        cascade="all, delete-orphan",
        foreign_keys="Report.user_id",
    )

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
