"""Artwork CRUD and interactions."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from extensions import db
from forms import ArtworkForm, CommentForm, ReportForm
from models import Artwork, Category, Comment, Favourite, Like, Report, Share
from routes.helpers import admin_required

artwork_bp = Blueprint("artwork", __name__)


def _store_artwork_file(uploaded_file) -> str:
    original = secure_filename(uploaded_file.filename or "")
    suffix = Path(original).suffix.lower()
    filename = f"{uuid4().hex}{suffix}"
    destination = Path(current_app.config["ARTWORK_UPLOAD_FOLDER"]) / filename
    uploaded_file.save(destination)
    return filename


@artwork_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = ArtworkForm()
    form.category_id.choices = [(category.id, category.name) for category in Category.query.order_by(Category.name.asc()).all()]
    if form.validate_on_submit():
        if not form.image.data and not (form.video_url.data or "").strip():
            flash("Please upload an image or add a video URL.", "warning")
            return render_template("artwork/form.html", form=form, page_title="Upload Artwork")
        filename = _store_artwork_file(form.image.data) if form.image.data else ""
        title_slug = "-".join(form.title.data.lower().strip().split())
        artwork = Artwork(
            title=form.title.data,
            slug=f"{title_slug}-{uuid4().hex[:8]}",
            description=form.description.data,
            filename=filename,
            video_url=(form.video_url.data or "").strip(),
            user_id=current_user.id,
            category_id=form.category_id.data,
            status="pending",
        )
        db.session.add(artwork)
        db.session.commit()
        flash("Artwork uploaded and sent for review.", "success")
        return redirect(url_for("artwork.submitted", slug=artwork.slug))
    return render_template("artwork/form.html", form=form, page_title="Upload Artwork")


@artwork_bp.route("/<string:slug>", methods=["GET", "POST"])
def detail(slug: str):
    artwork = Artwork.query.filter_by(slug=slug).first_or_404()
    comment_form = CommentForm()
    report_form = ReportForm()

    if comment_form.validate_on_submit() and current_user.is_authenticated and request.form.get("form_name") == "comment":
        comment = Comment(content=comment_form.content.data, user_id=current_user.id, artwork_id=artwork.id)
        db.session.add(comment)
        db.session.commit()
        flash("Comment posted.", "success")
        return redirect(url_for("artwork.detail", slug=artwork.slug))

    recent_likers = (
        Like.query.filter_by(artwork_id=artwork.id)
        .order_by(Like.created_at.desc())
        .join(Like.user)
        .limit(8)
        .all()
    )
    recent_sharers = (
        Share.query.filter_by(artwork_id=artwork.id)
        .order_by(Share.created_at.desc())
        .join(Share.user)
        .limit(8)
        .all()
    )
    return render_template(
        "artwork/detail.html",
        artwork=artwork,
        comment_form=comment_form,
        report_form=report_form,
        recent_likers=recent_likers,
        recent_sharers=recent_sharers,
    )


@artwork_bp.route("/<string:slug>/submitted")
@login_required
def submitted(slug: str):
    artwork = Artwork.query.filter_by(slug=slug).first_or_404()
    if artwork.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template("artwork/submitted.html", artwork=artwork)


@artwork_bp.route("/<string:slug>/edit", methods=["GET", "POST"])
@login_required
def edit(slug: str):
    artwork = Artwork.query.filter_by(slug=slug).first_or_404()
    if artwork.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    form = ArtworkForm(obj=artwork)
    form.category_id.choices = [(category.id, category.name) for category in Category.query.order_by(Category.name.asc()).all()]
    if form.validate_on_submit():
        artwork.title = form.title.data
        artwork.description = form.description.data
        artwork.category_id = form.category_id.data
        artwork.video_url = (form.video_url.data or "").strip()
        if form.image.data:
            artwork.filename = _store_artwork_file(form.image.data)
        if not artwork.filename and not artwork.video_url:
            flash("Please keep an image or video URL on the post.", "warning")
            return render_template("artwork/form.html", form=form, page_title="Edit Artwork")
        artwork.status = "pending"
        db.session.commit()
        flash("Artwork updated and re-submitted for review.", "success")
        return redirect(url_for("artwork.detail", slug=artwork.slug))
    return render_template("artwork/form.html", form=form, page_title="Edit Artwork")


@artwork_bp.route("/<string:slug>/delete", methods=["POST"])
@login_required
def delete(slug: str):
    artwork = Artwork.query.filter_by(slug=slug).first_or_404()
    if artwork.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    db.session.delete(artwork)
    db.session.commit()
    flash("Artwork deleted.", "info")
    return redirect(url_for("main.gallery"))


@artwork_bp.route("/<string:slug>/like", methods=["POST"])
@login_required
def toggle_like(slug: str):
    artwork = Artwork.query.filter_by(slug=slug).first_or_404()
    like = Like.query.filter_by(user_id=current_user.id, artwork_id=artwork.id).first()
    if like:
        db.session.delete(like)
        flash("Like removed.", "info")
    else:
        db.session.add(Like(user_id=current_user.id, artwork_id=artwork.id))
        flash("Artwork liked.", "success")
    db.session.commit()
    return redirect(url_for("artwork.detail", slug=slug))


@artwork_bp.route("/<string:slug>/favourite", methods=["POST"])
@login_required
def toggle_favourite(slug: str):
    artwork = Artwork.query.filter_by(slug=slug).first_or_404()
    favourite = Favourite.query.filter_by(user_id=current_user.id, artwork_id=artwork.id).first()
    if favourite:
        db.session.delete(favourite)
        flash("Removed from favourites.", "info")
    else:
        db.session.add(Favourite(user_id=current_user.id, artwork_id=artwork.id))
        flash("Saved to favourites.", "success")
    db.session.commit()
    return redirect(url_for("artwork.detail", slug=slug))


@artwork_bp.route("/<string:slug>/share", methods=["POST"])
@login_required
def share(slug: str):
    artwork = Artwork.query.filter_by(slug=slug).first_or_404()
    existing = Share.query.filter_by(user_id=current_user.id, artwork_id=artwork.id).first()
    if existing:
        flash("You already shared this artwork.", "info")
    else:
        db.session.add(Share(user_id=current_user.id, artwork_id=artwork.id))
        db.session.commit()
        flash("Share recorded. You can now send the link to others.", "success")
    return redirect(url_for("artwork.detail", slug=slug))


@artwork_bp.route("/<string:slug>/report", methods=["POST"])
@login_required
def report(slug: str):
    artwork = Artwork.query.filter_by(slug=slug).first_or_404()
    report_form = ReportForm()
    if report_form.validate_on_submit():
        db.session.add(
            Report(
                reason=report_form.reason.data,
                details=report_form.details.data or "",
                user_id=current_user.id,
                artwork_id=artwork.id,
            )
        )
        db.session.commit()
        flash("Report submitted for review.", "success")
    else:
        flash("Please complete the report form.", "warning")
    return redirect(url_for("artwork.detail", slug=slug))


@artwork_bp.route("/<string:slug>/download")
def download(slug: str):
    artwork = Artwork.query.filter_by(slug=slug, status="approved").first_or_404()
    if not artwork.filename:
        flash("This post does not include a downloadable image.", "info")
        return redirect(url_for("artwork.detail", slug=slug))
    artwork.download_count += 1
    db.session.commit()
    return send_from_directory(current_app.config["ARTWORK_UPLOAD_FOLDER"], artwork.filename, as_attachment=True)
