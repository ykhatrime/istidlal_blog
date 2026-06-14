"""Admin content form and query services."""
from __future__ import annotations

from flask import request

from app.models.article import Article
from app.models.comment import Comment
from app.models.project import Project
from app.models.tag import Tag
from app.models.user import User
from app.security import clean_html, clean_text, safe_external_url
from app.services.upload_service import save_uploaded_image


def active_articles_query():
    return Article.query.filter(Article.deleted_at.is_(None))


def active_projects_query():
    return Project.query.filter(Project.deleted_at.is_(None))


def active_comments_query():
    return Comment.query.filter(Comment.deleted_at.is_(None))


def bool_form(name: str) -> bool:
    return request.form.get(name) == 'on'


def selected_tags_from_form():
    tag_ids = request.form.getlist('tag_ids')
    if not tag_ids:
        return []
    return Tag.query.filter(Tag.id.in_(tag_ids)).all()


def assign_article_from_form(item: Article) -> Article:
    item.title_ar = clean_text(request.form.get('title_ar'), 220)
    item.title_en = clean_text(request.form.get('title_en'), 220)
    item.slug = clean_text(request.form.get('slug'), 260)
    item.excerpt_ar = clean_html(request.form.get('excerpt_ar'))
    item.excerpt_en = clean_html(request.form.get('excerpt_en'))
    item.content_ar = clean_html(request.form.get('content_ar'))
    item.content_en = clean_html(request.form.get('content_en'))
    item.seo_title_ar = clean_text(request.form.get('seo_title_ar'), 220)
    item.seo_title_en = clean_text(request.form.get('seo_title_en'), 220)
    item.seo_description_ar = clean_text(request.form.get('seo_description_ar'), 320)
    item.seo_description_en = clean_text(request.form.get('seo_description_en'), 320)
    item.canonical_url = safe_external_url(request.form.get('canonical_url'))
    item.og_image = clean_text(request.form.get('og_image'), 255)
    item.category_id = request.form.get('category_id') or None
    item.author_id = item.author_id or (User.query.first().id if User.query.first() else None)
    item.is_featured = bool_form('is_featured')
    item.is_published = bool_form('is_published')
    item.tags = selected_tags_from_form()

    uploaded_image = save_uploaded_image(request.files.get('image_file'), 'articles')
    item.image = uploaded_image or clean_text(request.form.get('image'), 255) or item.image or 'images/article-python.svg'
    if not item.og_image:
        item.og_image = item.image
    return item


def assign_project_from_form(item: Project) -> Project:
    item.title_ar = clean_text(request.form.get('title_ar'), 220)
    item.title_en = clean_text(request.form.get('title_en'), 220)
    item.slug = clean_text(request.form.get('slug'), 260)
    item.excerpt_ar = clean_html(request.form.get('excerpt_ar'))
    item.excerpt_en = clean_html(request.form.get('excerpt_en'))
    item.description_ar = clean_html(request.form.get('description_ar'))
    item.description_en = clean_html(request.form.get('description_en'))
    item.seo_title_ar = clean_text(request.form.get('seo_title_ar'), 220)
    item.seo_title_en = clean_text(request.form.get('seo_title_en'), 220)
    item.seo_description_ar = clean_text(request.form.get('seo_description_ar'), 320)
    item.seo_description_en = clean_text(request.form.get('seo_description_en'), 320)
    item.canonical_url = safe_external_url(request.form.get('canonical_url'))
    item.og_image = clean_text(request.form.get('og_image'), 255)
    item.technologies = clean_text(request.form.get('technologies'), 255)
    item.demo_url = safe_external_url(request.form.get('demo_url'))
    item.repo_url = safe_external_url(request.form.get('repo_url'))
    item.category_id = request.form.get('category_id') or None
    item.tags = selected_tags_from_form()
    item.is_featured = bool_form('is_featured')
    item.is_published = bool_form('is_published')

    uploaded_image = save_uploaded_image(request.files.get('image_file'), 'projects')
    item.image = uploaded_image or clean_text(request.form.get('image'), 255) or item.image or 'images/project-dashboard.svg'
    if not item.og_image:
        item.og_image = item.image
    return item
