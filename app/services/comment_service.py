"""Private comment workflow services."""
from __future__ import annotations

from flask import flash, g, request

from app.extensions import db
from app.models.comment import Comment
from app.security import clean_text, normalize_email
from app.utils.request_utils import client_ip


def save_private_comment(content_type: str, item) -> bool:
    """Store visitor feedback privately; it is never rendered publicly."""
    if request.form.get('website'):
        flash('تم استلام التعليق بنجاح.' if g.lang == 'ar' else 'Your comment has been received.', 'success')
        return True

    raw_comment = request.form.get('comment', '')
    name = clean_text(request.form.get('name'), 120)
    email = normalize_email(request.form.get('email'), required=False)
    comment_text = clean_text(raw_comment, 3000)

    if len(raw_comment) > 3000:
        flash('التعليق طويل جداً. الحد الأقصى 3000 حرف.' if g.lang == 'ar' else 'Comment is too long. Maximum is 3000 characters.', 'danger')
        return False
    if email is None:
        flash('يرجى إدخال بريد إلكتروني صحيح أو ترك الحقل فارغًا.' if g.lang == 'ar' else 'Please enter a valid email or leave it empty.', 'danger')
        return False
    if not name or not comment_text:
        flash('يرجى إدخال الاسم والتعليق.' if g.lang == 'ar' else 'Please enter your name and comment.', 'danger')
        return False

    comment = Comment(
        content_type=content_type,
        article_id=item.id if content_type == 'article' else None,
        project_id=item.id if content_type == 'project' else None,
        name=name,
        email=email or None,
        comment=comment_text,
        status=Comment.STATUS_NEW,
        is_read=False,
        ip_address=client_ip(),
        user_agent=clean_text(request.headers.get('User-Agent', ''), 255),
    )
    db.session.add(comment)
    db.session.commit()
    flash('تم إرسال تعليقك، وسيظهر لصاحب الموقع فقط في لوحة التحكم.' if g.lang == 'ar' else 'Your comment was sent and will be visible only to the site owner in the admin dashboard.', 'success')
    return True
