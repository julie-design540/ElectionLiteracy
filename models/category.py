"""Artwork categories."""

from __future__ import annotations

from datetime import datetime

from extensions import db


class Category(db.Model):
    """A simple category used to group civic education artwork."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, default="")
    is_default = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    artworks = db.relationship("Artwork", back_populates="category")

    @staticmethod
    def slugify(name: str) -> str:
        return "-".join(name.lower().strip().split())

    @classmethod
    def get_or_create(cls, name: str, description: str = "", is_default: bool = True):
        slug = cls.slugify(name)
        category = cls.query.filter_by(slug=slug).first()
        if category is None:
            category = cls(name=name, slug=slug, description=description, is_default=is_default)
            db.session.add(category)
        else:
            category.description = category.description or description
        return category
