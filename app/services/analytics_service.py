"""Privacy-aware visitor analytics service.

The service is intentionally lightweight and internal-first:
- It tracks successful public HTML GET requests only.
- It excludes admin/auth/static/upload/system URLs.
- It stores hashed identifiers instead of raw IP addresses.
- It keeps route functions thin by centralising page classification and KPIs here.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from hashlib import sha256
import hmac
from urllib.parse import urlparse
from uuid import uuid4

from flask import current_app, g, request
from sqlalchemy import desc, func

from app.extensions import db
from app.models.article import Article
from app.models.page_view import PageView
from app.models.project import Project
from app.utils.request_utils import client_ip

VISITOR_COOKIE = 'istidlal_visitor_id'
COOKIE_MAX_AGE = 60 * 60 * 24 * 365
EXCLUDED_PREFIXES = ('/static/', '/uploads/')
SYSTEM_ENDPOINTS = {'static', 'robots_txt', 'sitemap_xml'}
PUBLIC_ENDPOINT_PREFIX = 'main.'


def _utc_day_start(value: datetime | None = None) -> datetime:
    value = value or datetime.utcnow()
    return value.replace(hour=0, minute=0, second=0, microsecond=0)


def _hmac_hash(value: str | None) -> str | None:
    if not value:
        return None
    secret = current_app.config.get('ANALYTICS_HASH_SECRET') or current_app.config.get('SECRET_KEY') or 'analytics-secret'
    return hmac.new(str(secret).encode('utf-8'), str(value).encode('utf-8'), sha256).hexdigest()


def _clean(value: str | None, limit: int) -> str | None:
    if not value:
        return None
    value = str(value).strip()
    return value[:limit] if value else None


def should_track_response(response) -> bool:
    if not current_app.config.get('INTERNAL_ANALYTICS_ENABLED', True):
        return False
    if current_app.config.get('ANALYTICS_RESPECT_DNT', True) and request.headers.get('DNT') == '1':
        return False
    if request.method != 'GET':
        return False
    if response.status_code < 200 or response.status_code >= 400:
        return False
    if not (response.content_type or '').startswith('text/html'):
        return False
    if any(request.path.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return False
    endpoint = request.endpoint or ''
    if endpoint in SYSTEM_ENDPOINTS:
        return False
    if endpoint.startswith('admin.') or endpoint.startswith('auth.'):
        return False
    return endpoint.startswith(PUBLIC_ENDPOINT_PREFIX)


def _visitor_id_from_request() -> tuple[str, bool]:
    visitor_id = request.cookies.get(VISITOR_COOKIE)
    if visitor_id:
        return visitor_id, False
    visitor_id = uuid4().hex
    g.analytics_visitor_id = visitor_id
    g.analytics_new_visitor = True
    return visitor_id, True


def set_visitor_cookie_if_needed(response):
    visitor_id = getattr(g, 'analytics_visitor_id', None)
    if visitor_id and getattr(g, 'analytics_new_visitor', False):
        response.set_cookie(
            VISITOR_COOKIE,
            visitor_id,
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            secure=current_app.config.get('SESSION_COOKIE_SECURE', False),
            samesite=current_app.config.get('SESSION_COOKIE_SAMESITE', 'Lax'),
        )
    return response


def _classify_current_page() -> tuple[str, int | None, str | None]:
    endpoint = request.endpoint or ''
    view_args = request.view_args or {}

    if endpoint == 'main.article_detail':
        article = Article.query.filter_by(slug=view_args.get('slug')).first()
        return 'article', article.id if article else None, article.title(getattr(g, 'lang', 'ar')) if article else None
    if endpoint == 'main.project_detail':
        project = Project.query.filter_by(slug=view_args.get('slug')).first()
        return 'project', project.id if project else None, project.title(getattr(g, 'lang', 'ar')) if project else None

    page_map = {
        'main.home': 'home',
        'main.articles': 'articles_index',
        'main.projects': 'projects_index',
        'main.explore': 'explore',
        'main.services': 'services',
        'main.about': 'about',
        'main.contact': 'contact',
    }
    page_type = page_map.get(endpoint, 'page')
    return page_type, None, None


def track_page_view(response) -> None:
    if not should_track_response(response):
        return
    try:
        visitor_id, _is_new = _visitor_id_from_request()
        page_type, page_id, page_title = _classify_current_page()
        db.session.add(PageView(
            path=_clean(request.path, 500) or '/',
            endpoint=_clean(request.endpoint, 120),
            page_type=page_type,
            page_id=page_id,
            page_title=_clean(page_title, 255),
            visitor_hash=_hmac_hash(visitor_id),
            ip_hash=_hmac_hash(client_ip()),
            user_agent=_clean(request.headers.get('User-Agent'), 255),
            referrer=_clean(request.referrer, 500),
            language=getattr(g, 'lang', None),
            status_code=response.status_code,
        ))
        db.session.commit()
    except Exception as exc:  # pragma: no cover - analytics should never break content delivery
        db.session.rollback()
        current_app.logger.warning('Unable to record page view: %s', exc)


def _distinct_visitors_since(start: datetime | None = None) -> int:
    query = PageView.query
    if start:
        query = query.filter(PageView.created_at >= start)
    return query.with_entities(PageView.visitor_hash).distinct().count()


def get_analytics_snapshot() -> dict:
    today = _utc_day_start()
    month = today.replace(day=1)
    return {
        'total_views': PageView.query.count(),
        'today_views': PageView.query.filter(PageView.created_at >= today).count(),
        'today_unique_visitors': _distinct_visitors_since(today),
        'month_views': PageView.query.filter(PageView.created_at >= month).count(),
        'month_unique_visitors': _distinct_visitors_since(month),
        'total_unique_visitors': _distinct_visitors_since(),
    }


def _daily_counts(days: int) -> list[dict]:
    days = max(1, min(days, 365))
    today = _utc_day_start()
    start = today - timedelta(days=days - 1)
    rows = PageView.query.filter(PageView.created_at >= start).with_entities(
        PageView.created_at,
        PageView.visitor_hash,
    ).all()
    views_by_day: dict[str, int] = defaultdict(int)
    visitors_by_day: dict[str, set[str]] = defaultdict(set)
    for created_at, visitor_hash in rows:
        key = created_at.strftime('%Y-%m-%d')
        views_by_day[key] += 1
        visitors_by_day[key].add(visitor_hash)

    max_views = max(views_by_day.values(), default=1)
    data = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        key = day.strftime('%Y-%m-%d')
        views = views_by_day.get(key, 0)
        data.append({
            'date': key,
            'label': day.strftime('%d/%m'),
            'views': views,
            'visitors': len(visitors_by_day.get(key, set())),
            'height': max(4, round((views / max_views) * 100)) if max_views else 4,
        })
    return data


def _top_pages(days: int, limit: int = 10) -> list[dict]:
    start = _utc_day_start() - timedelta(days=max(1, min(days, 365)) - 1)
    rows = PageView.query.filter(PageView.created_at >= start).with_entities(
        PageView.path,
        PageView.page_type,
        PageView.page_title,
        func.count(PageView.id).label('views'),
        func.count(func.distinct(PageView.visitor_hash)).label('visitors'),
    ).group_by(PageView.path, PageView.page_type, PageView.page_title).order_by(desc('views')).limit(limit).all()
    return [
        {
            'path': row.path,
            'page_type': row.page_type,
            'title': row.page_title or row.path,
            'views': int(row.views or 0),
            'visitors': int(row.visitors or 0),
        }
        for row in rows
    ]


def _referrer_domain(referrer: str | None) -> str:
    if not referrer:
        return 'Direct'
    host = urlparse(referrer).netloc.lower()
    if not host:
        return 'Direct'
    if host.startswith('www.'):
        host = host[4:]
    return host


def _top_referrers(days: int, limit: int = 8) -> list[dict]:
    start = _utc_day_start() - timedelta(days=max(1, min(days, 365)) - 1)
    rows = PageView.query.filter(PageView.created_at >= start).with_entities(PageView.referrer).all()
    counter = Counter(_referrer_domain(row.referrer) for row in rows)
    return [{'source': source, 'views': views} for source, views in counter.most_common(limit)]


def get_analytics_report(days: int = 30) -> dict:
    days = max(1, min(days or 30, 365))
    recent_views = PageView.query.order_by(PageView.created_at.desc()).limit(20).all()
    return {
        'days': days,
        'snapshot': get_analytics_snapshot(),
        'daily': _daily_counts(days),
        'top_pages': _top_pages(days),
        'top_referrers': _top_referrers(days),
        'recent_views': recent_views,
    }
