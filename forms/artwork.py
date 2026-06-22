"""Artwork-related forms."""

from __future__ import annotations

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import SelectField, SubmitField, TextAreaField, StringField
from wtforms.validators import InputRequired, Length, Optional


class ArtworkForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), Length(min=3, max=150)])
    description = TextAreaField("Description", validators=[InputRequired(), Length(min=10, max=3000)])
    category_id = SelectField("Category", coerce=int, validators=[InputRequired()])
    image = FileField("Artwork Image", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only.")])
    video_url = StringField("Video URL", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Save Artwork")


class CommentForm(FlaskForm):
    content = TextAreaField("Comment", validators=[InputRequired(), Length(min=2, max=500)])
    submit = SubmitField("Post Comment")


class ReportForm(FlaskForm):
    reason = SelectField(
        "Reason",
        choices=[
            ("copyright", "Copyright issue"),
            ("misleading", "Misleading civic information"),
            ("inappropriate", "Inappropriate content"),
            ("other", "Other"),
        ],
        validators=[InputRequired()],
    )
    details = TextAreaField("Details", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Submit Report")
