"""Artwork comments."""

from __future__ import annotations

from datetime import datetime

from extensions import db


class Comment(db.Model):
    """User comments attached to artwork items."""

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_moderated = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey("artworks.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    author = db.relationship("User", back_populates="comments")
    artwork = db.relationship("Artwork", back_populates="comments")
