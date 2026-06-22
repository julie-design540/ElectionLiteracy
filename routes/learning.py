"""Learning course routes."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from extensions import db
from forms import LessonForm
from models import Lesson, LessonProgress

learning_bp = Blueprint("learning", __name__)


def _store_lesson_upload(uploaded_file) -> str:
    """Persist an uploaded learning asset and return the stored filename."""

    original = secure_filename(uploaded_file.filename or "")
    suffix = Path(original).suffix.lower()
    filename = f"{uuid4().hex}{suffix}"
    destination = Path(current_app.config["LESSON_UPLOAD_FOLDER"]) / filename
    uploaded_file.save(destination)
    return filename


def _slugify(value: str) -> str:
    return "-".join(value.lower().strip().split())


def _lesson_progress_for(user_id: int, lesson_id: int) -> LessonProgress | None:
    return LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()


@learning_bp.route("/")
def index():
    lessons = Lesson.query.order_by(Lesson.order.asc(), Lesson.created_at.asc()).all()
    total_lessons = len(lessons)
    completed_lessons = 0
    progress_map: dict[int, LessonProgress] = {}
    continue_lesson = lessons[0] if lessons else None

    if current_user.is_authenticated and lessons:
        progress_entries = LessonProgress.query.filter_by(user_id=current_user.id).all()
        progress_map = {progress.lesson_id: progress for progress in progress_entries}
        completed_lessons = sum(1 for progress in progress_entries if progress.completed)
        continue_lesson = next((lesson for lesson in lessons if lesson.id not in progress_map or not progress_map[lesson.id].completed), lessons[0])

    progress_percent = round((completed_lessons / max(total_lessons, 1)) * 100, 0)
    featured_lessons = lessons[:3]
    return render_template(
        "learning/index.html",
        lessons=lessons,
        featured_lessons=featured_lessons,
        progress_map=progress_map,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        progress_percent=progress_percent,
        continue_lesson=continue_lesson,
    )


@learning_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = LessonForm()
    if form.validate_on_submit():
        cover_image = _store_lesson_upload(form.cover_image.data) if form.cover_image.data else ""
        attachment_filename = _store_lesson_upload(form.attachment.data) if form.attachment.data else ""
        attachment_label = form.attachment_label.data or (form.attachment.data.filename if form.attachment.data else "")
        slug = f"{_slugify(form.title.data)}-{uuid4().hex[:8]}"
        lesson = Lesson(
            title=form.title.data,
            slug=slug,
            summary=form.summary.data,
            content=form.content.data,
            order=form.order.data,
            estimated_minutes=form.estimated_minutes.data,
            video_url=(form.video_url.data or "").strip(),
            cover_image=cover_image,
            attachment_filename=attachment_filename,
            attachment_label=attachment_label,
            user_id=current_user.id,
        )
        db.session.add(lesson)
        db.session.commit()
        flash("Lesson published successfully.", "success")
        return redirect(url_for("learning.detail", slug=lesson.slug))
    return render_template("learning/form.html", form=form, page_title="Create Lesson")


@learning_bp.route("/<string:slug>")
def detail(slug: str):
    lesson = Lesson.query.filter_by(slug=slug).first_or_404()
    progress = None
    if current_user.is_authenticated:
        progress = _lesson_progress_for(current_user.id, lesson.id)
        if progress is None:
            progress = LessonProgress(user_id=current_user.id, lesson_id=lesson.id)
            db.session.add(progress)
        progress.last_viewed_at = datetime.utcnow()
        db.session.commit()

    next_lesson = (
        Lesson.query.filter(Lesson.order > lesson.order).order_by(Lesson.order.asc(), Lesson.created_at.asc()).first()
    )
    previous_lesson = (
        Lesson.query.filter(Lesson.order < lesson.order).order_by(Lesson.order.desc(), Lesson.created_at.desc()).first()
    )
    course_progress = 0
    total_lessons = Lesson.query.count()
    completed_lessons = 0
    if current_user.is_authenticated:
        completed_lessons = LessonProgress.query.filter_by(user_id=current_user.id, completed=True).count()
        course_progress = round((completed_lessons / max(total_lessons, 1)) * 100, 0)

    return render_template(
        "learning/detail.html",
        lesson=lesson,
        progress=progress,
        previous_lesson=previous_lesson,
        next_lesson=next_lesson,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        course_progress=course_progress,
    )


@learning_bp.route("/<string:slug>/progress", methods=["POST"])
@login_required
def progress(slug: str):
    lesson = Lesson.query.filter_by(slug=slug).first_or_404()
    progress = _lesson_progress_for(current_user.id, lesson.id)
    if progress is None:
        progress = LessonProgress(user_id=current_user.id, lesson_id=lesson.id)
        db.session.add(progress)
    mark_completed = request.form.get("completed", "1") == "1"
    if mark_completed and request.form.get("reached_end") != "1":
        flash("Read through the final page before marking this lesson complete.", "warning")
        return redirect(url_for("learning.detail", slug=lesson.slug))
    progress.completed = mark_completed
    progress.last_viewed_at = datetime.utcnow()
    db.session.commit()
    flash("Lesson progress updated.", "success")
    return redirect(url_for("learning.detail", slug=lesson.slug))


@learning_bp.route("/<string:slug>/edit", methods=["GET", "POST"])
@login_required
def edit(slug: str):
    lesson = Lesson.query.filter_by(slug=slug).first_or_404()
    if lesson.user_id not in (None, current_user.id) and not current_user.is_admin:
        abort(403)

    form = LessonForm(obj=lesson)
    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.summary = form.summary.data
        lesson.content = form.content.data
        lesson.order = form.order.data
        lesson.estimated_minutes = form.estimated_minutes.data
        lesson.video_url = (form.video_url.data or "").strip()
        lesson.attachment_label = form.attachment_label.data or lesson.attachment_label
        if form.cover_image.data:
            lesson.cover_image = _store_lesson_upload(form.cover_image.data)
        if form.attachment.data:
            lesson.attachment_filename = _store_lesson_upload(form.attachment.data)
            lesson.attachment_label = form.attachment_label.data or form.attachment.data.filename
        db.session.commit()
        flash("Lesson updated.", "success")
        return redirect(url_for("learning.detail", slug=lesson.slug))
    return render_template("learning/form.html", form=form, page_title="Edit Lesson")


@learning_bp.route("/<string:slug>/delete", methods=["POST"])
@login_required
def delete(slug: str):
    lesson = Lesson.query.filter_by(slug=slug).first_or_404()
    if lesson.user_id not in (None, current_user.id) and not current_user.is_admin:
        abort(403)
    db.session.delete(lesson)
    db.session.commit()
    flash("Lesson removed.", "info")
    return redirect(url_for("learning.index"))


@learning_bp.route("/files/<string:filename>")
def file(filename: str):
    return send_from_directory(current_app.config["LESSON_UPLOAD_FOLDER"], filename, as_attachment=True)
