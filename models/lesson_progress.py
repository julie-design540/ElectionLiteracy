"""Lesson progress tracking model."""

from __future__ import annotations

from datetime import datetime

from extensions import db


class LessonProgress(db.Model):
    """Tracks a user's progress through lessons."""

    __tablename__ = "lesson_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    last_viewed_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="lesson_progress")
    lesson = db.relationship("Lesson", back_populates="progresses")

    __table_args__ = (db.UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_progress"),)
