"""Authentication-related forms."""

from __future__ import annotations

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import Email, EqualTo, InputRequired, Length, Optional


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password", message="Passwords must match.")]
    )
    profile_image = FileField("Profile Image", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"])])
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    identifier = StringField("Username or Email", validators=[InputRequired(), Length(min=3, max=120)])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class ForgotPasswordForm(FlaskForm):
    email = StringField("Account Email", validators=[InputRequired(), Email(), Length(max=120)])
    submit = SubmitField("Send Reset Link")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[InputRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password", message="Passwords must match.")]
    )
    submit = SubmitField("Reset Password")


class ProfileForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=120)])
    bio = TextAreaField("Bio", validators=[Optional(), Length(max=500)])
    profile_image = FileField("Profile Image", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"])])
    submit = SubmitField("Save Profile")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[InputRequired()])
    new_password = PasswordField("New Password", validators=[InputRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("new_password", message="Passwords must match.")]
    )
    submit = SubmitField("Update Password")
