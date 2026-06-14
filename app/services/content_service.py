"""Query and content-domain services.

Routes should stay thin. This module owns common filtering, sorting, sidebar,
and related-content logic for articles and projects.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import or_

from app.models.article import Article
from app.models.project import Project
from app.models.category import Category
from app.models.tag import Tag

VALID_SORTS = {'newest', 'oldest', 'title', 'views', 'featured'}


@dataclass(frozen=True)
class ContentFilters:
    q: str = ''
    category_slug: str = ''
    tag_slug: str = ''
    sort: str = 'newest'
    selected_category: Category | None = None
    selected_tag: Tag | None = None


def published_articles_query():
    return Article.query.filter(Article.is_published.is_(True), Article.deleted_at.is_(None))


def published_projects_query():
    return Project.query.filter(Project.is_published.is_(True), Project.deleted_at.is_(None))


def normalize_sort(value: str | None, default: str = 'newest') -> str:
    value = (value or default).strip() or default
    return value if value in VALID_SORTS else default


def build_filters(args, default_sort: str = 'newest') -> ContentFilters:
    category_slug = (args.get('category') or '').strip()
    tag_slug = (args.get('tag') or '').strip()
    return ContentFilters(
        q=(args.get('q') or '').strip(),
        category_slug=category_slug,
        tag_slug=tag_slug,
        sort=normalize_sort(args.get('sort'), default_sort),
        selected_category=Category.query.filter_by(slug=category_slug).first() if category_slug else None,
        selected_tag=Tag.query.filter_by(slug=tag_slug).first() if tag_slug else None,
    )


def split_search_terms(q: str) -> list[str]:
    return [term for term in (q or '').replace('،', ' ').replace(',', ' ').split() if term]


def apply_article_filters(query, filters: ContentFilters):
    if filters.selected_category:
        query = query.filter(Article.category_id == filters.selected_category.id)
    if filters.selected_tag:
        query = query.filter(Article.tags.any(id=filters.selected_tag.id))

    for term in split_search_terms(filters.q):
        like = f'%{term}%'
        query = query.filter(or_(
            Article.title_ar.ilike(like),
            Article.title_en.ilike(like),
            Article.excerpt_ar.ilike(like),
            Article.excerpt_en.ilike(like),
            Article.content_ar.ilike(like),
            Article.content_en.ilike(like),
            Article.seo_title_ar.ilike(like),
            Article.seo_title_en.ilike(like),
            Article.category.has(Category.name_ar.ilike(like)),
            Article.category.has(Category.name_en.ilike(like)),
            Article.tags.any(Tag.name.ilike(like)),
        ))
    return query


def apply_project_filters(query, filters: ContentFilters):
    if filters.selected_category:
        query = query.filter(Project.category_id == filters.selected_category.id)
    if filters.selected_tag:
        query = query.filter(Project.tags.any(id=filters.selected_tag.id))

    for term in split_search_terms(filters.q):
        like = f'%{term}%'
        query = query.filter(or_(
            Project.title_ar.ilike(like),
            Project.title_en.ilike(like),
            Project.excerpt_ar.ilike(like),
            Project.excerpt_en.ilike(like),
            Project.description_ar.ilike(like),
            Project.description_en.ilike(like),
            Project.seo_title_ar.ilike(like),
            Project.seo_title_en.ilike(like),
            Project.technologies.ilike(like),
            Project.category.has(Category.name_ar.ilike(like)),
            Project.category.has(Category.name_en.ilike(like)),
            Project.tags.any(Tag.name.ilike(like)),
        ))
    return query


def apply_article_sort(query, sort: str = 'newest'):
    if sort == 'oldest':
        return query.order_by(Article.created_at.asc())
    if sort == 'title':
        return query.order_by(Article.title_ar.asc())
    if sort == 'views':
        return query.order_by(Article.views.desc(), Article.created_at.desc())
    if sort == 'featured':
        return query.order_by(Article.is_featured.desc(), Article.created_at.desc())
    return query.order_by(Article.created_at.desc())


def apply_project_sort(query, sort: str = 'newest'):
    if sort == 'oldest':
        return query.order_by(Project.created_at.asc())
    if sort == 'title':
        return query.order_by(Project.title_ar.asc())
    if sort == 'featured':
        return query.order_by(Project.is_featured.desc(), Project.created_at.desc())
    return query.order_by(Project.created_at.desc())


def get_sidebar_data():
    categories = Category.query.order_by(Category.name_ar.asc()).all()
    category_counts = {}
    for category in categories:
        articles_count = published_articles_query().filter(Article.category_id == category.id).count()
        projects_count = published_projects_query().filter(Project.category_id == category.id).count()
        category_counts[category.id] = articles_count + projects_count

    tags = Tag.query.order_by(Tag.name.asc()).limit(18).all()
    tag_counts = {}
    for tag in tags:
        articles_count = published_articles_query().filter(Article.tags.any(id=tag.id)).count()
        projects_count = published_projects_query().filter(Project.tags.any(id=tag.id)).count()
        tag_counts[tag.id] = articles_count + projects_count

    return categories, category_counts, tags, tag_counts


def template_filter_context(filters: ContentFilters):
    categories, category_counts, tags, tag_counts = get_sidebar_data()
    return {
        'q': filters.q,
        'sort': filters.sort,
        'selected_category': filters.selected_category,
        'selected_tag': filters.selected_tag,
        'categories': categories,
        'category_counts': category_counts,
        'tags': tags,
        'tag_counts': tag_counts,
        'has_filters': bool(filters.q or filters.selected_category or filters.selected_tag or filters.sort not in ['newest']),
    }


def _extend_unique(items, candidates, limit: int):
    seen = {item.id for item in items}
    for item in candidates:
        if item.id not in seen:
            items.append(item)
            seen.add(item.id)
        if len(items) >= limit:
            break
    return items


def get_related_articles(article: Article, limit: int = 3):
    related = []
    base = published_articles_query().filter(Article.id != article.id)
    if article.category_id:
        related = _extend_unique(
            related,
            base.filter(Article.category_id == article.category_id).order_by(Article.views.desc(), Article.created_at.desc()).limit(limit).all(),
            limit,
        )
    tag_ids = [tag.id for tag in article.tags]
    if len(related) < limit and tag_ids:
        related = _extend_unique(
            related,
            base.filter(Article.tags.any(Tag.id.in_(tag_ids))).order_by(Article.views.desc(), Article.created_at.desc()).limit(limit).all(),
            limit,
        )
    if len(related) < limit:
        related = _extend_unique(related, base.order_by(Article.views.desc(), Article.created_at.desc()).limit(limit).all(), limit)
    return related[:limit]


def get_related_projects(project: Project, limit: int = 3):
    related = []
    base = published_projects_query().filter(Project.id != project.id)
    if project.category_id:
        related = _extend_unique(
            related,
            base.filter(Project.category_id == project.category_id).order_by(Project.is_featured.desc(), Project.created_at.desc()).limit(limit).all(),
            limit,
        )
    tag_ids = [tag.id for tag in project.tags]
    if len(related) < limit and tag_ids:
        related = _extend_unique(
            related,
            base.filter(Project.tags.any(Tag.id.in_(tag_ids))).order_by(Project.is_featured.desc(), Project.created_at.desc()).limit(limit).all(),
            limit,
        )
    if len(related) < limit:
        related = _extend_unique(related, base.order_by(Project.is_featured.desc(), Project.created_at.desc()).limit(limit).all(), limit)
    return related[:limit]
