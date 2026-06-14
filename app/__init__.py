from pathlib import Path

from flask import Flask, Response, g, redirect, render_template, request, url_for

from config import get_config
from .extensions import csrf, db, limiter, migrate
from .translations import get_translations


def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or get_config())

    _ensure_runtime_directories(app)
    _register_extensions(app)
    _register_blueprints(app)
    _register_request_hooks(app)
    _register_template_context(app)
    _register_error_handlers(app)
    _register_core_routes(app)
    _register_cli(app)

    return app


def _ensure_runtime_directories(app):
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)


def _register_extensions(app):
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)


def _register_blueprints(app):
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/<lang>/auth')
    app.register_blueprint(admin_bp, url_prefix='/<lang>/admin')


def _register_request_hooks(app):
    @app.before_request
    def set_language():
        lang = request.view_args.get('lang') if request.view_args else None
        if lang not in app.config['LANGUAGES']:
            lang = app.config['DEFAULT_LANG']
        g.lang = lang
        g.is_rtl = lang == 'ar'
        g.t = get_translations(lang)

    @app.after_request
    def finalize_response(response):
        from app.services.analytics_service import set_visitor_cookie_if_needed, track_page_view

        if app.config.get('SECURITY_HEADERS_ENABLED', True):
            response.headers.setdefault('X-Content-Type-Options', 'nosniff')
            response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
            response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
            response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')

        track_page_view(response)
        set_visitor_cookie_if_needed(response)
        return response


def _asset_url(path, fallback='images/placeholder-data.svg', external=False):
    """Return a safe URL for uploaded/static/external images."""
    if not path:
        return url_for('static', filename=fallback, _external=external)
    if str(path).startswith(('http://', 'https://', '//')):
        return path
    clean = str(path).lstrip('/')
    if clean.startswith('app/static/'):
        clean = clean.replace('app/static/', '', 1)
    if clean.startswith('static/'):
        clean = clean.replace('static/', '', 1)
    return url_for('static', filename=clean, _external=external)


def _switch_lang_url():
    target = 'en' if getattr(g, 'lang', 'ar') == 'ar' else 'ar'
    args = request.view_args.copy() if request.view_args else {}
    args['lang'] = target
    try:
        return url_for(request.endpoint, **args, **request.args)
    except Exception:
        return url_for('main.home', lang=target)


def _register_template_context(app):
    @app.context_processor
    def inject_globals():
        return {
            'lang': getattr(g, 'lang', app.config['DEFAULT_LANG']),
            'is_rtl': getattr(g, 'is_rtl', True),
            't': getattr(g, 't', get_translations('ar')),
            'asset_url': _asset_url,
            'switch_lang_url': _switch_lang_url,
        }


def _register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403


def _register_core_routes(app):
    @app.route('/')
    def root():
        return redirect(url_for('main.home', lang=app.config['DEFAULT_LANG']))

    @app.route('/robots.txt')
    def robots_txt():
        body = f"User-agent: *\nAllow: /\nSitemap: {url_for('sitemap_xml', _external=True)}\n"
        return Response(body, mimetype='text/plain')

    @app.route('/sitemap.xml')
    def sitemap_xml():
        from app.models.article import Article
        from app.models.project import Project

        urls = []
        for lang_code in app.config['LANGUAGES']:
            urls.extend([
                url_for('main.home', lang=lang_code, _external=True),
                url_for('main.articles', lang=lang_code, _external=True),
                url_for('main.projects', lang=lang_code, _external=True),
                url_for('main.services', lang=lang_code, _external=True),
                url_for('main.explore', lang=lang_code, _external=True),
                url_for('main.about', lang=lang_code, _external=True),
                url_for('main.contact', lang=lang_code, _external=True),
            ])
            for article in Article.query.filter(Article.is_published.is_(True), Article.deleted_at.is_(None)).all():
                urls.append(url_for('main.article_detail', lang=lang_code, slug=article.slug, _external=True))
            for project in Project.query.filter(Project.is_published.is_(True), Project.deleted_at.is_(None)).all():
                urls.append(url_for('main.project_detail', lang=lang_code, slug=project.slug, _external=True))
        xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for item in sorted(set(urls)):
            xml.append(f'<url><loc>{item}</loc></url>')
        xml.append('</urlset>')
        return Response('\n'.join(xml), mimetype='application/xml')


def _register_cli(app):
    from app.cli import register_commands

    register_commands(app)
