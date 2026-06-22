"""Authentication routes."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_required, login_user, logout_user
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import func, or_
from werkzeug.utils import secure_filename

from extensions import db
from forms import ChangePasswordForm, ForgotPasswordForm, LoginForm, ProfileForm, RegisterForm, ResetPasswordForm
from models import Artwork, Comment, Favourite, Lesson, LessonProgress, Like, Share, User

auth_bp = Blueprint("auth", __name__)

PASSWORD_RESET_SALT = "password-reset"


def _save_profile_image(uploaded_file) -> str:
    filename = secure_filename(uploaded_file.filename or "")
    if not filename:
        return ""
    destination = Path(current_app.config["PROFILE_UPLOAD_FOLDER"]) / filename
    uploaded_file.save(destination)
    return filename


def _password_reset_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=PASSWORD_RESET_SALT)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter(or_(User.username == form.username.data, User.email == form.email.data)).first():
            flash("Username or email already exists.", "warning")
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            if form.profile_image.data:
                user.profile_image = _save_profile_image(form.profile_image.data)
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(or_(User.username == form.identifier.data, User.email == form.identifier.data)).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid login details.", "danger")
        else:
            login_user(user)
            flash("Welcome back.", "success")
            return redirect(request.args.get("next") or url_for("main.home"))
    return render_template("auth/login.html", form=form)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("auth.profile"))

    form = ForgotPasswordForm()
    reset_url = None
    if form.validate_on_submit():
        user = User.query.filter(func.lower(User.email) == form.email.data.strip().lower()).first()
        if user:
            token = _password_reset_serializer().dumps({"user_id": user.id})
            reset_url = url_for("auth.reset_password", token=token, _external=True)
        flash("If that email exists, a password reset link has been prepared.", "info")
    return render_template("auth/forgot_password.html", form=form, reset_url=reset_url)


@auth_bp.route("/reset-password/<string:token>", methods=["GET", "POST"])
def reset_password(token: str):
    if current_user.is_authenticated:
        return redirect(url_for("auth.profile"))

    try:
        data = _password_reset_serializer().loads(token, max_age=3600)
    except SignatureExpired:
        flash("Password reset link has expired. Request a new one.", "warning")
        return redirect(url_for("auth.forgot_password"))
    except BadSignature:
        flash("Password reset link is invalid.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user = db.session.get(User, data.get("user_id"))
    if user is None:
        flash("Password reset account was not found.", "danger")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Password reset successfully. Log in with the new password.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))


@auth_bp.route("/profile")
@login_required
def profile():
    artworks = current_user.artworks
    favourites = [item.artwork for item in current_user.favourites]
    lessons_created = current_user.lessons
    lesson_progress_entries = LessonProgress.query.filter_by(user_id=current_user.id).all()
    lesson_progress_map = {progress.lesson_id: progress for progress in lesson_progress_entries}
    ordered_lessons = Lesson.query.order_by(Lesson.order.asc(), Lesson.created_at.asc()).all()
    completed_lessons = sum(1 for progress in lesson_progress_entries if progress.completed)
    total_lessons = Lesson.query.count()
    learning_progress = round((completed_lessons / max(total_lessons, 1)) * 100, 0)
    continue_lesson = next(
        (lesson for lesson in ordered_lessons if lesson.id not in lesson_progress_map or not lesson_progress_map[lesson.id].completed),
        ordered_lessons[0] if ordered_lessons else None,
    )
    engagement_stats = {
        "likes_received": db.session.query(func.count(Like.id))
        .join(Artwork, Like.artwork_id == Artwork.id)
        .filter(Artwork.user_id == current_user.id)
        .scalar(),
        "shares_received": db.session.query(func.count(Share.id))
        .join(Artwork, Share.artwork_id == Artwork.id)
        .filter(Artwork.user_id == current_user.id)
        .scalar(),
        "downloads_received": db.session.query(func.coalesce(func.sum(Artwork.download_count), 0))
        .filter(Artwork.user_id == current_user.id)
        .scalar(),
        "comments_received": db.session.query(func.count(Comment.id))
        .join(Artwork, Comment.artwork_id == Artwork.id)
        .filter(Artwork.user_id == current_user.id)
        .scalar(),
        "lessons_created": len(lessons_created),
        "lessons_completed": completed_lessons,
    }
    total_engagements = (
        engagement_stats["likes_received"]
        + engagement_stats["shares_received"]
        + engagement_stats["downloads_received"]
        + engagement_stats["comments_received"]
    )
    engagement_stats["average_interactions_per_post"] = round(total_engagements / max(len(artworks), 1), 1)
    top_artworks = sorted(
        artworks,
        key=lambda item: (item.like_count + item.share_count + item.download_count + item.favourite_count, item.created_at),
        reverse=True,
    )[:3]
    return render_template(
        "auth/profile.html",
        artworks=artworks,
        favourites=favourites,
        lessons_created=lessons_created,
        lesson_progress_entries=lesson_progress_entries,
        engagement_stats=engagement_stats,
        top_artworks=top_artworks,
        learning_progress=learning_progress,
        continue_lesson=continue_lesson,
        total_lessons=total_lessons,
    )


@auth_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        duplicate = User.query.filter(
            or_(User.username == form.username.data, User.email == form.email.data)
        ).filter(User.id != current_user.id).first()
        if duplicate:
            flash("Username or email is already in use.", "warning")
            return render_template("auth/edit_profile.html", form=form)
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data or ""
        if form.profile_image.data:
            current_user.profile_image = _save_profile_image(form.profile_image.data)
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("auth.profile"))
    return render_template("auth/edit_profile.html", form=form)


@auth_bp.route("/profile/password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password updated successfully.", "success")
            return redirect(url_for("auth.profile"))
    return render_template("auth/change_password.html", form=form)
