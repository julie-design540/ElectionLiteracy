"""Public-facing pages."""

from __future__ import annotations

from flask import Blueprint, render_template, request
from flask_login import current_user

from models import Artwork, Category, Lesson, LessonProgress

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    featured = (
        Artwork.query.filter_by(status="approved", is_featured=True).order_by(Artwork.created_at.desc()).limit(6).all()
    )
    latest = Artwork.query.filter_by(status="approved").order_by(Artwork.created_at.desc()).limit(12).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    lessons = Lesson.query.order_by(Lesson.order.asc(), Lesson.created_at.asc()).all()
    completed_lessons = 0
    learning_progress = 0
    continue_lesson = lessons[0] if lessons else None
    if current_user.is_authenticated and lessons:
        progress_entries = LessonProgress.query.filter_by(user_id=current_user.id).all()
        progress_map = {progress.lesson_id: progress for progress in progress_entries}
        completed_lessons = sum(1 for progress in progress_entries if progress.completed)
        learning_progress = round((completed_lessons / max(len(lessons), 1)) * 100, 0)
        continue_lesson = next(
            (lesson for lesson in lessons if lesson.id not in progress_map or not progress_map[lesson.id].completed),
            lessons[0],
        )
    return render_template(
        "home.html",
        featured=featured,
        latest=latest,
        categories=categories,
        lessons=lessons,
        continue_lesson=continue_lesson,
        completed_lessons=completed_lessons,
        learning_progress=learning_progress,
    )


@main_bp.route("/gallery")
def gallery():
    query = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)
    sort = request.args.get("sort", "newest")

    artworks = Artwork.query.filter_by(status="approved")
    if query:
        search_term = f"%{query}%"
        artworks = artworks.filter(Artwork.title.ilike(search_term) | Artwork.description.ilike(search_term))
    if category_id:
        artworks = artworks.filter_by(category_id=category_id)
    if sort == "popular":
        artworks = artworks.order_by(Artwork.download_count.desc(), Artwork.created_at.desc())
    else:
        artworks = artworks.order_by(Artwork.created_at.desc())

    return render_template(
        "gallery.html",
        artworks=artworks.all(),
        categories=Category.query.order_by(Category.name.asc()).all(),
        query=query,
        selected_category=category_id,
        selected_sort=sort,
    )
