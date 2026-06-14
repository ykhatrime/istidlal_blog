import os
from pathlib import Path
from urllib.parse import quote_plus

BASE_DIR = Path(__file__).resolve().parent


def _bool_env(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def _normalize_database_url(url):
    """Normalize DB URL for SQLAlchemy."""
    if not url:
        return url
    if url.startswith('mysql://'):
        return url.replace('mysql://', 'mysql+pymysql://', 1)
    return url


def _mysql_uri_from_env():
    """Build a MySQL URI from MYSQL_* environment variables."""
    user = quote_plus(os.environ.get('MYSQL_USER', 'istidlal_user'))
    password = quote_plus(os.environ.get('MYSQL_PASSWORD', 'change-me'))
    host = os.environ.get('MYSQL_HOST', '127.0.0.1')
    port = os.environ.get('MYSQL_PORT', '3306')
    database = os.environ.get('MYSQL_DATABASE', 'istidlal_blog')
    charset = os.environ.get('MYSQL_CHARSET', 'utf8mb4')
    return f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}'


class BaseConfig:
    """Base configuration shared by all environments."""

    APP_ENV = os.environ.get('APP_ENV', os.environ.get('FLASK_ENV', 'development')).lower()
    IS_PRODUCTION = APP_ENV in {'production', 'prod'}

    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-secret-key')
    DEBUG = False
    TESTING = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '280')),
    }

    WTF_CSRF_TIME_LIMIT = int(os.environ.get('WTF_CSRF_TIME_LIMIT', '3600'))
    WTF_CSRF_SSL_STRICT = _bool_env('WTF_CSRF_SSL_STRICT', IS_PRODUCTION)

    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')

    UPLOAD_FOLDER = BASE_DIR / 'app' / 'static' / 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))
    ALLOWED_UPLOAD_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    LANGUAGES = ('ar', 'en')
    DEFAULT_LANG = os.environ.get('DEFAULT_LANG', 'ar')

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    SESSION_COOKIE_SECURE = _bool_env('SESSION_COOKIE_SECURE', IS_PRODUCTION)
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('PERMANENT_SESSION_LIFETIME', '43200'))

    SECURITY_HEADERS_ENABLED = _bool_env('SECURITY_HEADERS_ENABLED', True)

    INTERNAL_ANALYTICS_ENABLED = _bool_env('INTERNAL_ANALYTICS_ENABLED', True)
    ANALYTICS_RESPECT_DNT = _bool_env('ANALYTICS_RESPECT_DNT', True)
    ANALYTICS_HASH_SECRET = os.environ.get('ANALYTICS_HASH_SECRET', SECRET_KEY)


class DevelopmentConfig(BaseConfig):
    DEBUG = _bool_env('DEBUG', True)
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get('DATABASE_URL') or f"sqlite:///{BASE_DIR / 'instance' / 'datablog.sqlite'}"
    )


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(BaseConfig):
    DEBUG = _bool_env('DEBUG', False)
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.environ.get('DATABASE_URL')) or _mysql_uri_from_env()
    SESSION_COOKIE_SECURE = True


class Config(DevelopmentConfig):
    """Backward-compatible default used by create_app() when no config is passed."""


def get_config():
    env = os.environ.get('APP_ENV', os.environ.get('FLASK_ENV', 'development')).lower()
    if env in {'production', 'prod'}:
        return ProductionConfig
    if env in {'testing', 'test'}:
        return TestingConfig
    return DevelopmentConfig
