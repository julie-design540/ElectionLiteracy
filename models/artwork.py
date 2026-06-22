"""Artwork model."""

from __future__ import annotations

from datetime import datetime
from urllib.parse import parse_qs, urlparse

from extensions import db


class Artwork(db.Model):
    """A single uploaded civic education artwork item."""

    __tablename__ = "artworks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(255), default="", nullable=False)
    mime_type = db.Column(db.String(100), default="image/jpeg")
    video_url = db.Column(db.String(500), default="", nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    download_count = db.Column(db.Integer, default=0, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    author = db.relationship("User", back_populates="artworks")
    category = db.relationship("Category", back_populates="artworks")
    comments = db.relationship("Comment", back_populates="artwork", cascade="all, delete-orphan")
    likes = db.relationship("Like", back_populates="artwork", cascade="all, delete-orphan")
    shares = db.relationship("Share", back_populates="artwork", cascade="all, delete-orphan")
    favourites = db.relationship("Favourite", back_populates="artwork", cascade="all, delete-orphan")
    reports = db.relationship("Report", back_populates="artwork", cascade="all, delete-orphan")

    @property
    def like_count(self) -> int:
        return len(self.likes)

    @property
    def favourite_count(self) -> int:
        return len(self.favourites)

    @property
    def share_count(self) -> int:
        return len(self.shares)

    @property
    def has_video(self) -> bool:
        return bool(self.video_url)

    @property
    def video_embed_url(self) -> str:
        if not self.video_url:
            return ""
        parsed = urlparse(self.video_url)
        host = parsed.netloc.lower().replace("www.", "")
        if "youtube.com" in host:
            if parsed.path.startswith("/embed/"):
                return self.video_url
            if parsed.path.startswith("/shorts/"):
                video_id = parsed.path.split("/")[2]
                return f"https://www.youtube.com/embed/{video_id}"
            video_id = parse_qs(parsed.query).get("v", [""])[0]
            return f"https://www.youtube.com/embed/{video_id}" if video_id else self.video_url
        if "youtu.be" in host:
            video_id = parsed.path.strip("/")
            return f"https://www.youtube.com/embed/{video_id}" if video_id else self.video_url
        if "vimeo.com" in host:
            video_id = parsed.path.strip("/")
            return f"https://player.vimeo.com/video/{video_id}" if video_id else self.video_url
        return self.video_url
