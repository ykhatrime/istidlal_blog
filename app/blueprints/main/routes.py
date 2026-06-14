from flask import flash, g, redirect, render_template, request, url_for

from app.extensions import db, limiter
from app.models.article import Article
from app.models.message import ContactMessage
from app.models.newsletter import NewsletterSubscriber
from app.models.project import Project
from app.security import clean_text, normalize_email
from app.services.comment_service import save_private_comment
from app.services.content_service import (
    apply_article_filters,
    apply_article_sort,
    apply_project_filters,
    apply_project_sort,
    build_filters,
    get_related_articles,
    get_related_projects,
    get_sidebar_data,
    published_articles_query,
    published_projects_query,
    template_filter_context,
)
from app.services.offering_service import get_service_offerings, get_service_process
from app.utils.request_utils import client_ip

from . import main_bp


@main_bp.route('/')
def home(lang):
    articles = published_articles_query().order_by(Article.is_featured.desc(), Article.created_at.desc()).limit(3).all()
    projects = published_projects_query().order_by(Project.is_featured.desc(), Project.created_at.desc()).limit(3).all()
    articles_count = published_articles_query().count()
    projects_count = published_projects_query().count()
    categories, category_counts, tags, tag_counts = get_sidebar_data()
    return render_template(
        'main/home.html',
        articles=articles,
        projects=projects,
        articles_count=articles_count,
        projects_count=projects_count,
        categories=categories,
        category_counts=category_counts,
        tags=tags,
        tag_counts=tag_counts,
    )


@main_bp.route('/explore')
def explore(lang):
    content_type = request.args.get('type', 'all')
    if content_type not in ['all', 'articles', 'projects']:
        content_type = 'all'

    filters = build_filters(request.args)
    articles_query = apply_article_filters(published_articles_query(), filters)
    projects_query = apply_project_filters(published_projects_query(), filters)

    articles = apply_article_sort(articles_query, filters.sort).all() if content_type in ['all', 'articles'] else []
    project_sort = filters.sort if filters.sort != 'views' else 'newest'
    projects = apply_project_sort(projects_query, project_sort).all() if content_type in ['all', 'projects'] else []

    return render_template(
        'main/explore.html',
        content_type=content_type,
        articles=articles,
        projects=projects,
        **template_filter_context(filters),
    )


@main_bp.route('/articles')
def articles(lang):
    page = request.args.get('page', 1, type=int)
    filters = build_filters(request.args)
    query = apply_article_filters(published_articles_query(), filters)
    total_results = query.count()
    pagination = apply_article_sort(query, filters.sort).paginate(page=page, per_page=9, error_out=False)
    return render_template('main/articles.html', pagination=pagination, total_results=total_results, **template_filter_context(filters))


@main_bp.route('/articles/<slug>')
def article_detail(lang, slug):
    article = published_articles_query().filter_by(slug=slug).first_or_404()
    article.views += 1
    db.session.commit()
    related = get_related_articles(article)
    return render_template('main/article_detail.html', article=article, related=related)


@main_bp.route('/articles/<slug>/comments', methods=['POST'])
@limiter.limit('20 per hour', methods=['POST'])
@limiter.limit('3 per minute', methods=['POST'])
def article_comment(lang, slug):
    article = published_articles_query().filter_by(slug=slug).first_or_404()
    save_private_comment('article', article)
    return redirect(url_for('main.article_detail', lang=lang, slug=slug) + '#private-comment')


@main_bp.route('/projects')
def projects(lang):
    page = request.args.get('page', 1, type=int)
    filters = build_filters(request.args)
    project_sort = filters.sort if filters.sort != 'views' else 'newest'
    query = apply_project_filters(published_projects_query(), filters)
    total_results = query.count()
    pagination = apply_project_sort(query, project_sort).paginate(page=page, per_page=9, error_out=False)
    return render_template('main/projects.html', pagination=pagination, total_results=total_results, **template_filter_context(filters))


@main_bp.route('/projects/<slug>')
def project_detail(lang, slug):
    project = published_projects_query().filter_by(slug=slug).first_or_404()
    related = get_related_projects(project)
    return render_template('main/project_detail.html', project=project, related=related)


@main_bp.route('/projects/<slug>/comments', methods=['POST'])
@limiter.limit('20 per hour', methods=['POST'])
@limiter.limit('3 per minute', methods=['POST'])
def project_comment(lang, slug):
    project = published_projects_query().filter_by(slug=slug).first_or_404()
    save_private_comment('project', project)
    return redirect(url_for('main.project_detail', lang=lang, slug=slug) + '#private-comment')


@main_bp.route('/services')
def services(lang):
    offerings = get_service_offerings(lang)
    process_steps = get_service_process(lang)
    return render_template('main/services.html', offerings=offerings, process_steps=process_steps)


@main_bp.route('/about')
def about(lang):
    return render_template('main/about.html')


@main_bp.route('/contact', methods=['GET', 'POST'])
@limiter.limit('20 per hour', methods=['POST'])
@limiter.limit('3 per minute', methods=['POST'])
def contact(lang):
    if request.method == 'POST':
        email = normalize_email(request.form.get('email'), required=True)
        if email is None:
            flash('يرجى إدخال بريد إلكتروني صحيح.' if lang == 'ar' else 'Please enter a valid email.', 'danger')
            return redirect(url_for('main.contact', lang=lang))
        msg = ContactMessage(
            name=clean_text(request.form.get('name'), 160),
            email=email,
            subject=clean_text(request.form.get('subject'), 220),
            message=clean_text(request.form.get('message'), 3000),
            ip_address=client_ip(),
            user_agent=clean_text(request.headers.get('User-Agent', ''), 255),
        )
        if not msg.name or not msg.message:
            flash('يرجى تعبئة الاسم والرسالة.' if lang == 'ar' else 'Please fill name and message.', 'danger')
            return redirect(url_for('main.contact', lang=lang))
        db.session.add(msg)
        db.session.commit()
        flash(g.t['contact_success'], 'success')
        return redirect(url_for('main.contact', lang=lang))
    return render_template('main/contact.html')


@main_bp.route('/newsletter/subscribe', methods=['POST'])
@limiter.limit('50 per hour', methods=['POST'])
@limiter.limit('5 per minute', methods=['POST'])
def subscribe(lang):
    email = normalize_email(request.form.get('email'), required=True)
    if email is None:
        flash('يرجى إدخال بريد إلكتروني صحيح.' if lang == 'ar' else 'Please enter a valid email.', 'danger')
        return redirect(request.referrer or url_for('main.home', lang=lang))

    exists = NewsletterSubscriber.query.filter_by(email=email).first()
    if exists and not exists.deleted_at:
        flash(g.t['subscribe_exists'], 'info')
    elif exists and exists.deleted_at:
        exists.deleted_at = None
        exists.is_active = True
        db.session.commit()
        flash(g.t['subscribe_success'], 'success')
    else:
        db.session.add(NewsletterSubscriber(email=email))
        db.session.commit()
        flash(g.t['subscribe_success'], 'success')
    return redirect(request.referrer or url_for('main.home', lang=lang))
