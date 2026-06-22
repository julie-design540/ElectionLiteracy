"""Learning module forms."""

from __future__ import annotations

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, NumberRange, Optional


class LessonForm(FlaskForm):
    title = StringField("Lesson Title", validators=[InputRequired(), Length(min=3, max=150)])
    summary = StringField("Summary", validators=[InputRequired(), Length(min=10, max=255)])
    content = TextAreaField("Lesson Content", validators=[InputRequired(), Length(min=50, max=10000)])
    order = IntegerField("Sequence Order", validators=[InputRequired(), NumberRange(min=1, max=999)])
    estimated_minutes = IntegerField("Estimated Minutes", validators=[InputRequired(), NumberRange(min=5, max=240)])
    video_url = StringField("Video URL", validators=[Optional(), Length(max=500)])
    cover_image = FileField("Cover Image", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"])])
    attachment = FileField(
        "Lesson Resource",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp", "pdf", "doc", "docx"])],
    )
    attachment_label = StringField("Resource Label", validators=[Optional(), Length(max=120)])
    submit = SubmitField("Save Lesson")
