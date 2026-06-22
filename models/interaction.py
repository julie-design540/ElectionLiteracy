"""Lightweight interaction models: likes, shares, favourites and reports."""

from __future__ import annotations

from datetime import datetime

from extensions import db


class Like(db.Model):
    """A like from a user for a specific artwork."""

    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey("artworks.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="likes")
    artwork = db.relationship("Artwork", back_populates="likes")

    __table_args__ = (db.UniqueConstraint("user_id", "artwork_id", name="uq_like_user_artwork"),)


class Share(db.Model):
    """A share action from a user for a specific artwork."""

    __tablename__ = "shares"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey("artworks.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="shares")
    artwork = db.relationship("Artwork", back_populates="shares")

    __table_args__ = (db.UniqueConstraint("user_id", "artwork_id", name="uq_share_user_artwork"),)


class Favourite(db.Model):
    """A user's saved artwork."""

    __tablename__ = "favourites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey("artworks.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="favourites")
    artwork = db.relationship("Artwork", back_populates="favourites")

    __table_args__ = (db.UniqueConstraint("user_id", "artwork_id", name="uq_favourite_user_artwork"),)


class Report(db.Model):
    """A report submitted by a user about artwork or comments."""

    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="open", nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey("artworks.id"), nullable=False)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    reviewed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    reporter = db.relationship("User", foreign_keys=[user_id], back_populates="reports")
    reviewer = db.relationship("User", foreign_keys=[reviewed_by_id])
    artwork = db.relationship("Artwork", back_populates="reports")
