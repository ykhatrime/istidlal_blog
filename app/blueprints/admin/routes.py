from sqlalchemy import or_
from flask import flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash

from app.audit import log_admin_action
from app.extensions import db, limiter
from app.models.article import Article
from app.models.audit_log import AuditLog
from app.models.category import Category
from app.models.comment import Comment
from app.models.message import ContactMessage
from app.models.newsletter import NewsletterSubscriber
from app.models.project import Project
from app.models.tag import Tag
from app.models.user import User
from app.security import clean_text, normalize_email
from app.services.analytics_service import get_analytics_report, get_analytics_snapshot
from app.services.admin_content_service import (
    active_articles_query,
    active_comments_query,
    active_projects_query,
    assign_article_from_form,
    assign_project_from_form,
    bool_form,
)
from app.services.permission_service import permission_required
from app.services.upload_service import save_uploaded_image

from . import admin_bp


@admin_bp.route('/')
@permission_required('view_admin')
def dashboard(lang):
    stats = {
        'articles': active_articles_query().count(),
        'projects': active_projects_query().count(),
        'subscribers': NewsletterSubscriber.query.filter(NewsletterSubscriber.deleted_at.is_(None)).count(),
        'messages': ContactMessage.query.filter(ContactMessage.deleted_at.is_(None)).count(),
        'comments': active_comments_query().count(),
        'unread_comments': active_comments_query().filter(Comment.status == Comment.STATUS_NEW).count(),
        'categories': Category.query.count(),
        'tags': Tag.query.count(),
    }
    stats.update(get_analytics_snapshot())
    latest_messages = ContactMessage.query.filter(ContactMessage.deleted_at.is_(None)).order_by(ContactMessage.created_at.desc()).limit(5).all()
    latest_comments = active_comments_query().order_by(Comment.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, latest_messages=latest_messages, latest_comments=latest_comments)


@admin_bp.route('/articles')
@permission_required('manage_content')
def articles(lang):
    items = active_articles_query().order_by(Article.created_at.desc()).all()
    return render_template('admin/articles.html', items=items)


@admin_bp.route('/articles/new', methods=['GET', 'POST'])
@admin_bp.route('/articles/<int:item_id>/edit', methods=['GET', 'POST'])
@permission_required('manage_content')
def article_form(lang, item_id=None):
    item = active_articles_query().filter_by(id=item_id).first_or_404() if item_id else Article()
    categories = Category.query.order_by(Category.name_ar.asc()).all()
    tags = Tag.query.order_by(Tag.name.asc()).all()

    if request.method == 'POST':
        assign_article_from_form(item)
        if not item.title_ar or not item.title_en or not item.slug:
            flash('يرجى تعبئة العنوان والرمز.' if lang == 'ar' else 'Please fill title and slug.', 'error')
            return render_template('admin/article_form.html', item=item, categories=categories, tags=tags)

        db.session.add(item)
        action = 'update_article' if item_id else 'create_article'
        db.session.flush()
        log_admin_action(action, 'Article', item.id, item.slug)
        db.session.commit()
        flash('تم حفظ المقال بنجاح' if lang == 'ar' else 'Article saved successfully', 'success')
        return redirect(url_for('admin.articles', lang=lang))

    return render_template('admin/article_form.html', item=item, categories=categories, tags=tags)


@admin_bp.route('/articles/<int:item_id>/delete', methods=['POST'])
@permission_required('manage_content')
def delete_article(lang, item_id):
    item = active_articles_query().filter_by(id=item_id).first_or_404()
    item.soft_delete(session.get('user_id'))
    active_comments_query().filter_by(article_id=item.id).update({'status': Comment.STATUS_ARCHIVED, 'is_read': True})
    log_admin_action('soft_delete_article', 'Article', item.id, item.slug)
    db.session.commit()
    flash('تم أرشفة المقال بدل حذفه نهائيًا.' if lang == 'ar' else 'Article archived instead of permanently deleted.', 'success')
    return redirect(url_for('admin.articles', lang=lang))


@admin_bp.route('/projects')
@permission_required('manage_content')
def projects(lang):
    items = active_projects_query().order_by(Project.created_at.desc()).all()
    return render_template('admin/projects.html', items=items)


@admin_bp.route('/projects/new', methods=['GET', 'POST'])
@admin_bp.route('/projects/<int:item_id>/edit', methods=['GET', 'POST'])
@permission_required('manage_content')
def project_form(lang, item_id=None):
    item = active_projects_query().filter_by(id=item_id).first_or_404() if item_id else Project()
    categories = Category.query.order_by(Category.name_ar.asc()).all()
    tags = Tag.query.order_by(Tag.name.asc()).all()

    if request.method == 'POST':
        assign_project_from_form(item)
        if not item.title_ar or not item.title_en or not item.slug:
            flash('يرجى تعبئة العنوان والرمز.' if lang == 'ar' else 'Please fill title and slug.', 'error')
            return render_template('admin/project_form.html', item=item, categories=categories, tags=tags)

        db.session.add(item)
        action = 'update_project' if item_id else 'create_project'
        db.session.flush()
        log_admin_action(action, 'Project', item.id, item.slug)
        db.session.commit()
        flash('تم حفظ المشروع بنجاح' if lang == 'ar' else 'Project saved successfully', 'success')
        return redirect(url_for('admin.projects', lang=lang))

    return render_template('admin/project_form.html', item=item, categories=categories, tags=tags)


@admin_bp.route('/projects/<int:item_id>/delete', methods=['POST'])
@permission_required('manage_content')
def delete_project(lang, item_id):
    item = active_projects_query().filter_by(id=item_id).first_or_404()
    item.soft_delete(session.get('user_id'))
    active_comments_query().filter_by(project_id=item.id).update({'status': Comment.STATUS_ARCHIVED, 'is_read': True})
    log_admin_action('soft_delete_project', 'Project', item.id, item.slug)
    db.session.commit()
    flash('تم أرشفة المشروع بدل حذفه نهائيًا.' if lang == 'ar' else 'Project archived instead of permanently deleted.', 'success')
    return redirect(url_for('admin.projects', lang=lang))


@admin_bp.route('/coding', methods=['GET', 'POST'])
@permission_required('manage_content')
def coding(lang):
    """Manage categories and tags. Arabic label: الترميز."""
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        item_id = request.form.get('item_id')

        if form_type == 'category':
            item = Category.query.get(item_id) if item_id else Category()
            item.name_ar = clean_text(request.form.get('name_ar'), 120)
            item.name_en = clean_text(request.form.get('name_en'), 120)
            item.slug = clean_text(request.form.get('slug'), 160)
            item.description = clean_text(request.form.get('description'), 500)
            item.color = clean_text(request.form.get('color'), 30) or '#2563eb'
            if item.name_ar and item.name_en and item.slug:
                db.session.add(item)
                db.session.flush()
                log_admin_action('save_category', 'Category', item.id, item.slug)
                db.session.commit()
                flash('تم حفظ القسم بنجاح' if lang == 'ar' else 'Category saved successfully', 'success')
            else:
                flash('يرجى تعبئة اسم القسم والرمز' if lang == 'ar' else 'Please fill category names and slug', 'error')

        elif form_type == 'tag':
            item = Tag.query.get(item_id) if item_id else Tag()
            item.name = clean_text(request.form.get('name'), 80)
            item.slug = clean_text(request.form.get('slug'), 100)
            if item.name and item.slug:
                db.session.add(item)
                db.session.flush()
                log_admin_action('save_tag', 'Tag', item.id, item.slug)
                db.session.commit()
                flash('تم حفظ الكلمة المفتاحية بنجاح' if lang == 'ar' else 'Tag saved successfully', 'success')
            else:
                flash('يرجى تعبئة اسم الكلمة المفتاحية والرمز' if lang == 'ar' else 'Please fill tag name and slug', 'error')

        return redirect(url_for('admin.coding', lang=lang))

    categories = Category.query.order_by(Category.name_ar.asc()).all()
    tags = Tag.query.order_by(Tag.name.asc()).all()
    return render_template('admin/coding.html', categories=categories, tags=tags)


@admin_bp.route('/coding/category/<int:item_id>/delete', methods=['POST'])
@permission_required('manage_content')
def delete_category(lang, item_id):
    item = Category.query.get_or_404(item_id)
    if item.articles or item.projects:
        flash('لا يمكن حذف القسم لأنه مرتبط بمقالات أو مشروعات' if lang == 'ar' else 'Cannot delete category because it is used by articles or projects', 'error')
    else:
        log_admin_action('delete_category', 'Category', item.id, item.slug)
        db.session.delete(item)
        db.session.commit()
        flash('تم حذف القسم' if lang == 'ar' else 'Category deleted', 'success')
    return redirect(url_for('admin.coding', lang=lang))


@admin_bp.route('/coding/tag/<int:item_id>/delete', methods=['POST'])
@permission_required('manage_content')
def delete_tag(lang, item_id):
    item = Tag.query.get_or_404(item_id)
    log_admin_action('delete_tag', 'Tag', item.id, item.slug)
    db.session.delete(item)
    db.session.commit()
    flash('تم حذف الكلمة المفتاحية' if lang == 'ar' else 'Tag deleted', 'success')
    return redirect(url_for('admin.coding', lang=lang))


@admin_bp.route('/upload-image', methods=['POST'])
@permission_required('manage_content')
@limiter.limit('20 per minute', methods=['POST'])
def upload_image(lang):
    uploaded = save_uploaded_image(request.files.get('image'), 'editor')
    if not uploaded:
        return jsonify({'success': False, 'message': 'Upload failed'}), 400
    db.session.commit()
    return jsonify({'success': True, 'url': url_for('static', filename=uploaded)})


@admin_bp.route('/newsletter')
@permission_required('manage_newsletter')
def newsletter(lang):
    items = NewsletterSubscriber.query.filter(NewsletterSubscriber.deleted_at.is_(None)).order_by(NewsletterSubscriber.created_at.desc()).all()
    return render_template('admin/newsletter.html', items=items)


@admin_bp.route('/newsletter/<int:item_id>/toggle', methods=['POST'])
@permission_required('manage_newsletter')
def toggle_subscriber(lang, item_id):
    item = NewsletterSubscriber.query.filter(NewsletterSubscriber.deleted_at.is_(None), NewsletterSubscriber.id == item_id).first_or_404()
    item.is_active = not item.is_active
    log_admin_action('toggle_subscriber', 'NewsletterSubscriber', item.id, item.email)
    db.session.commit()
    return redirect(url_for('admin.newsletter', lang=lang))


@admin_bp.route('/newsletter/<int:item_id>/delete', methods=['POST'])
@permission_required('manage_newsletter')
def delete_subscriber(lang, item_id):
    item = NewsletterSubscriber.query.filter(NewsletterSubscriber.deleted_at.is_(None), NewsletterSubscriber.id == item_id).first_or_404()
    item.soft_delete(session.get('user_id'))
    log_admin_action('soft_delete_subscriber', 'NewsletterSubscriber', item.id, item.email)
    db.session.commit()
    return redirect(url_for('admin.newsletter', lang=lang))


@admin_bp.route('/comments')
@permission_required('manage_comments')
def comments(lang):
    content_type = request.args.get('type', 'all')
    status = request.args.get('status', 'all')
    q = request.args.get('q', '').strip()
    article_id = request.args.get('article_id', type=int)
    project_id = request.args.get('project_id', type=int)

    query = active_comments_query()
    if content_type in ['article', 'project']:
        query = query.filter(Comment.content_type == content_type)
    if article_id:
        query = query.filter(Comment.article_id == article_id)
    if project_id:
        query = query.filter(Comment.project_id == project_id)
    if status in Comment.VALID_STATUSES:
        query = query.filter(Comment.status == status)
    elif status == 'unread':
        query = query.filter(Comment.status == Comment.STATUS_NEW)
    elif status == 'read':
        query = query.filter(Comment.status == Comment.STATUS_READ)
    if q:
        like = f'%{q}%'
        query = query.filter(or_(Comment.name.ilike(like), Comment.email.ilike(like), Comment.comment.ilike(like)))

    items = query.order_by(Comment.created_at.desc()).all()
    return render_template('admin/comments.html', items=items, content_type=content_type, status=status, q=q)


@admin_bp.route('/comments/<int:item_id>/status', methods=['POST'])
@permission_required('manage_comments')
def update_comment_status(lang, item_id):
    item = active_comments_query().filter_by(id=item_id).first_or_404()
    status = request.form.get('status', Comment.STATUS_READ)
    item.set_status(status)
    item.internal_note = clean_text(request.form.get('internal_note'), 2000) or item.internal_note
    log_admin_action('update_comment_status', 'Comment', item.id, status)
    db.session.commit()
    flash('تم تحديث حالة التعليق' if lang == 'ar' else 'Comment status updated', 'success')
    return redirect(request.referrer or url_for('admin.comments', lang=lang))


@admin_bp.route('/comments/<int:item_id>/toggle-read', methods=['POST'])
@permission_required('manage_comments')
def toggle_comment_read(lang, item_id):
    item = active_comments_query().filter_by(id=item_id).first_or_404()
    item.set_status(Comment.STATUS_NEW if item.status == Comment.STATUS_READ else Comment.STATUS_READ)
    log_admin_action('toggle_comment_read', 'Comment', item.id, item.status)
    db.session.commit()
    flash('تم تحديث حالة التعليق' if lang == 'ar' else 'Comment status updated', 'success')
    return redirect(request.referrer or url_for('admin.comments', lang=lang))


@admin_bp.route('/comments/<int:item_id>/delete', methods=['POST'])
@permission_required('manage_comments')
def delete_comment(lang, item_id):
    item = active_comments_query().filter_by(id=item_id).first_or_404()
    item.soft_delete(session.get('user_id'))
    log_admin_action('soft_delete_comment', 'Comment', item.id, item.content_type)
    db.session.commit()
    flash('تم أرشفة التعليق بدل حذفه نهائيًا' if lang == 'ar' else 'Comment archived instead of permanently deleted', 'success')
    return redirect(request.referrer or url_for('admin.comments', lang=lang))


@admin_bp.route('/comments/mark-all-read', methods=['POST'])
@permission_required('manage_comments')
def mark_all_comments_read(lang):
    active_comments_query().filter(Comment.status == Comment.STATUS_NEW).update({'status': Comment.STATUS_READ, 'is_read': True})
    log_admin_action('mark_all_comments_read', 'Comment', None, 'all new comments')
    db.session.commit()
    flash('تم تعليم جميع التعليقات كمقروءة' if lang == 'ar' else 'All comments marked as read', 'success')
    return redirect(url_for('admin.comments', lang=lang))


@admin_bp.route('/messages')
@permission_required('view_messages')
def messages(lang):
    items = ContactMessage.query.filter(ContactMessage.deleted_at.is_(None)).order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', items=items)


@admin_bp.route('/users')
@permission_required('manage_users')
def users(lang):
    items = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', items=items, roles=sorted(User.VALID_ROLES))


@admin_bp.route('/users/new', methods=['POST'])
@permission_required('manage_users')
def create_user(lang):
    username = clean_text(request.form.get('username'), 80)
    email = normalize_email(request.form.get('email'), required=True)
    password = request.form.get('password', '')
    role = request.form.get('role', User.ROLE_VIEWER)
    if not username or email is None or not password:
        flash('يرجى تعبئة اسم المستخدم والبريد وكلمة المرور بشكل صحيح.' if lang == 'ar' else 'Please provide valid username, email, and password.', 'error')
        return redirect(url_for('admin.users', lang=lang))
    if User.query.filter(or_(User.username == username, User.email == email)).first():
        flash('اسم المستخدم أو البريد مستخدم مسبقًا.' if lang == 'ar' else 'Username or email already exists.', 'error')
        return redirect(url_for('admin.users', lang=lang))
    item = User(username=username, email=email, password_hash=generate_password_hash(password), role=role if role in User.VALID_ROLES else User.ROLE_VIEWER, is_active=bool_form('is_active'))
    db.session.add(item)
    db.session.flush()
    log_admin_action('create_user', 'User', item.id, item.role)
    db.session.commit()
    flash('تم إنشاء المستخدم' if lang == 'ar' else 'User created', 'success')
    return redirect(url_for('admin.users', lang=lang))


@admin_bp.route('/users/<int:item_id>/role', methods=['POST'])
@permission_required('manage_users')
def update_user_role(lang, item_id):
    item = User.query.get_or_404(item_id)
    item.set_role(request.form.get('role'))
    item.is_active = bool_form('is_active')
    new_password = request.form.get('new_password', '')
    if new_password:
        item.password_hash = generate_password_hash(new_password)
    log_admin_action('update_user_role', 'User', item.id, item.role)
    db.session.commit()
    flash('تم تحديث المستخدم' if lang == 'ar' else 'User updated', 'success')
    return redirect(url_for('admin.users', lang=lang))


@admin_bp.route('/audit')
@permission_required('view_audit')
def audit_logs(lang):
    items = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(200).all()
    return render_template('admin/audit_logs.html', items=items)


@admin_bp.route('/analytics')
@permission_required('view_analytics')
def analytics(lang):
    days = request.args.get('days', 30, type=int)
    report = get_analytics_report(days)
    return render_template('admin/analytics.html', report=report, days=report['days'])
