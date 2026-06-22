"""Admin dashboard and moderation routes."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import func

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from extensions import db
from forms import AdminUserForm, CategoryForm, ModerationForm, ReviewForm, UserRoleForm
from models import Artwork, Category, Comment, Lesson, LessonProgress, Report, User
from routes.helpers import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@admin_required
def dashboard():
    pending_artworks = Artwork.query.filter_by(status="pending").order_by(Artwork.created_at.desc()).limit(6).all()
    recent_artworks = Artwork.query.order_by(Artwork.created_at.desc()).limit(8).all()
    recent_reports = Report.query.order_by(Report.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_lessons = Lesson.query.order_by(Lesson.created_at.desc()).limit(5).all()
    category_breakdown = (
        db.session.query(Category.name, func.count(Artwork.id))
        .outerjoin(Artwork, Artwork.category_id == Category.id)
        .group_by(Category.id, Category.name)
        .order_by(func.count(Artwork.id).desc(), Category.name.asc())
        .limit(8)
        .all()
    )
    category_labels = [category_name for category_name, _total in category_breakdown]
    category_counts = [total for _category_name, total in category_breakdown]
    stats = {
        "users": User.query.count(),
        "artworks": Artwork.query.count(),
        "pending": Artwork.query.filter_by(status="pending").count(),
        "reports": Report.query.filter_by(status="open").count(),
        "approved": Artwork.query.filter_by(status="approved").count(),
        "rejected": Artwork.query.filter_by(status="rejected").count(),
        "lessons": Lesson.query.count(),
        "lesson_progress": LessonProgress.query.count(),
        "lesson_completed": LessonProgress.query.filter_by(completed=True).count(),
    }
    status_labels = ["Pending", "Approved", "Rejected"]
    status_counts = [
        Artwork.query.filter_by(status="pending").count(),
        Artwork.query.filter_by(status="approved").count(),
        Artwork.query.filter_by(status="rejected").count(),
    ]
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        status_labels=status_labels,
        status_counts=status_counts,
        pending_artworks=pending_artworks,
        recent_artworks=recent_artworks,
        recent_reports=recent_reports,
        recent_users=recent_users,
        recent_lessons=recent_lessons,
        category_breakdown=category_breakdown,
        category_labels=category_labels,
        category_counts=category_counts,
        moderation_form=ModerationForm(),
    )


@admin_bp.route("/users", methods=["GET", "POST"])
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    forms = {user.id: UserRoleForm(prefix=f"user-{user.id}") for user in users}
    create_admin_form = AdminUserForm()

    for user in users:
        forms[user.id].role.data = user.role

    if request.method == "POST" and request.form.get("form_name") == "create_admin":
        if create_admin_form.validate_on_submit():
            duplicate = User.query.filter(
                (func.lower(User.username) == create_admin_form.username.data.strip().lower())
                | (func.lower(User.email) == create_admin_form.email.data.strip().lower())
            ).first()
            if duplicate:
                flash("Username or email is already in use.", "warning")
            else:
                admin = User(
                    username=create_admin_form.username.data.strip(),
                    email=create_admin_form.email.data.strip().lower(),
                    role="admin",
                )
                admin.set_password(create_admin_form.password.data)
                db.session.add(admin)
                db.session.commit()
                flash("Admin user created.", "success")
                return redirect(url_for("admin.manage_users"))

    if request.method == "POST" and request.form.get("form_name") != "create_admin":
        user_id = request.form.get("user_id", type=int)
        form = forms.get(user_id)
        if form and form.validate():
            user = db.session.get(User, user_id)
            if user:
                user.role = form.role.data
                db.session.commit()
                flash("User role updated.", "success")
                return redirect(url_for("admin.manage_users"))

    return render_template("admin/users.html", users=users, forms=forms, create_admin_form=create_admin_form)


@admin_bp.route("/artworks")
@admin_required
def manage_artworks():
    artworks = Artwork.query.order_by(Artwork.created_at.desc()).all()
    moderation_form = ModerationForm()
    return render_template("admin/artworks.html", artworks=artworks, moderation_form=moderation_form)


@admin_bp.route("/artworks/<int:artwork_id>/moderate", methods=["POST"])
@admin_required
def moderate_artwork(artwork_id: int):
    artwork = db.session.get(Artwork, artwork_id)
    if artwork is None:
        flash("Artwork not found.", "danger")
        return redirect(url_for("admin.manage_artworks"))
    form = ModerationForm()
    if form.validate_on_submit():
        artwork.status = form.status.data
        db.session.commit()
        flash("Artwork status updated.", "success")
    return redirect(url_for("admin.manage_artworks"))


@admin_bp.route("/artworks/<int:artwork_id>/delete", methods=["POST"])
@admin_required
def delete_artwork(artwork_id: int):
    artwork = db.session.get(Artwork, artwork_id)
    if artwork is None:
        flash("Artwork not found.", "danger")
        return redirect(url_for("admin.manage_artworks"))

    filename = artwork.filename
    db.session.delete(artwork)
    db.session.commit()

    if filename:
        upload_folder = Path(current_app.config["ARTWORK_UPLOAD_FOLDER"])
        file_path = (upload_folder / filename).resolve()
        if upload_folder.resolve() in file_path.parents and file_path.exists():
            file_path.unlink()

    flash("Artwork post deleted.", "info")
    return redirect(url_for("admin.manage_artworks"))


@admin_bp.route("/comments")
@admin_required
def manage_comments():
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return render_template("admin/comments.html", comments=comments)


@admin_bp.route("/comments/<int:comment_id>/toggle", methods=["POST"])
@admin_required
def toggle_comment(comment_id: int):
    comment = db.session.get(Comment, comment_id)
    if comment:
        comment.is_moderated = not comment.is_moderated
        db.session.commit()
        flash("Comment moderation updated.", "success")
    return redirect(url_for("admin.manage_comments"))


@admin_bp.route("/categories", methods=["GET", "POST"])
@admin_required
def manage_categories():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category.get_or_create(form.name.data, form.description.data or "", form.is_default.data)
        category.description = form.description.data or category.description
        category.is_default = bool(form.is_default.data)
        db.session.commit()
        flash("Category saved.", "success")
        return redirect(url_for("admin.manage_categories"))

    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("admin/categories.html", categories=categories, form=form)


@admin_bp.route("/lessons")
@admin_required
def manage_lessons():
    lessons = Lesson.query.order_by(Lesson.order.asc(), Lesson.created_at.desc()).all()
    return render_template("admin/lessons.html", lessons=lessons)


@admin_bp.route("/lessons/<int:lesson_id>/delete", methods=["POST"])
@admin_required
def delete_lesson(lesson_id: int):
    lesson = db.session.get(Lesson, lesson_id)
    if lesson is None:
        flash("Lesson not found.", "danger")
        return redirect(url_for("admin.manage_lessons"))
    db.session.delete(lesson)
    db.session.commit()
    flash("Lesson deleted.", "info")
    return redirect(url_for("admin.manage_lessons"))


@admin_bp.route("/reports")
@admin_required
def view_reports():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    review_form = ReviewForm()
    return render_template("admin/reports.html", reports=reports, review_form=review_form)


@admin_bp.route("/reports/<int:report_id>", methods=["POST"])
@admin_required
def review_report(report_id: int):
    report = db.session.get(Report, report_id)
    if report is None:
        flash("Report not found.", "danger")
        return redirect(url_for("admin.view_reports"))
    form = ReviewForm()
    if form.validate_on_submit():
        report.status = form.status.data
        report.reviewed_by_id = request.form.get("reviewed_by_id", type=int) or None
        report.reviewed_at = datetime.utcnow()
        db.session.commit()
        flash("Report updated.", "success")
    return redirect(url_for("admin.view_reports"))
