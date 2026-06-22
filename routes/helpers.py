"""Shared route helpers."""

from __future__ import annotations

from functools import wraps

from flask import flash, redirect, request, url_for
from flask_login import current_user


def admin_required(view_func):
    """Protect a view so only admins can access it."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access the admin dashboard.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if not getattr(current_user, "is_admin", False):
            flash("Admin access required.", "danger")
            return redirect(url_for("main.home"))
        return view_func(*args, **kwargs)

    return wrapper
