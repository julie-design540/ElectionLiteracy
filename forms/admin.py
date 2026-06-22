"""Admin forms for moderation and management."""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import Email, EqualTo, InputRequired, Length, Optional


class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[InputRequired(), Length(min=3, max=100)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])
    is_default = BooleanField("Default category")
    submit = SubmitField("Save Category")


class ModerationForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[("approved", "Approve"), ("rejected", "Reject"), ("pending", "Keep Pending")],
        validators=[InputRequired()],
    )
    submit = SubmitField("Apply")


class ReviewForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[("open", "Open"), ("reviewed", "Reviewed"), ("closed", "Closed")],
        validators=[InputRequired()],
    )
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Update Report")


class UserRoleForm(FlaskForm):
    role = SelectField("Role", choices=[("user", "User"), ("admin", "Admin")], validators=[InputRequired()])
    submit = SubmitField("Update Role")


class AdminUserForm(FlaskForm):
    username = StringField("Admin Username", validators=[InputRequired(), Length(min=3, max=80)])
    email = StringField("Admin Email", validators=[InputRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password", message="Passwords must match.")]
    )
    submit = SubmitField("Create Admin")
