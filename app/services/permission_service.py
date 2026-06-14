"""Authentication and role permission helpers."""
from __future__ import annotations

from functools import wraps

from flask import abort, redirect, session, url_for

from app.models.user import User

ROLE_PERMISSIONS = {
    'admin': {'view_admin', 'manage_content', 'manage_comments', 'manage_newsletter', 'view_messages', 'manage_users', 'view_audit', 'view_analytics'},
    'editor': {'view_admin', 'manage_content', 'view_analytics'},
    'moderator': {'view_admin', 'manage_comments', 'view_messages', 'view_analytics'},
    'viewer': {'view_admin', 'view_analytics'},
}


def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


def user_has_permission(user, permission: str) -> bool:
    return bool(user and user.is_active and permission in ROLE_PERMISSIONS.get(user.role, set()))


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user or not user.is_active:
            session.clear()
            return redirect(url_for('auth.login', lang=kwargs.get('lang', 'ar')))
        return view(*args, **kwargs)
    return wrapped


def permission_required(permission: str):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user or not user.is_active:
                session.clear()
                return redirect(url_for('auth.login', lang=kwargs.get('lang', 'ar')))
            if not user_has_permission(user, permission):
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator
