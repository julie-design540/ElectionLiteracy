"""Learning lesson model."""

from __future__ import annotations

from datetime import datetime
from urllib.parse import parse_qs, urlparse

from extensions import db


class Lesson(db.Model):
    """A learning lesson for civic education."""

    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)
    summary = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0, nullable=False)
    estimated_minutes = db.Column(db.Integer, default=10, nullable=False)
    cover_image = db.Column(db.String(255), default="", nullable=False)
    attachment_filename = db.Column(db.String(255), default="", nullable=False)
    attachment_label = db.Column(db.String(120), default="", nullable=False)
    video_url = db.Column(db.String(500), default="", nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    author = db.relationship("User", back_populates="lessons")
    progresses = db.relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")

    @property
    def completion_count(self) -> int:
        return len(self.progresses)

    @property
    def completion_rate(self) -> float:
        if not self.progresses:
            return 0.0
        completed = sum(1 for progress in self.progresses if progress.completed)
        return round((completed / len(self.progresses)) * 100, 0)

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
