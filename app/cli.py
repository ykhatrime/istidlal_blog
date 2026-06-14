"""Application CLI commands.

Keeping commands outside run.py makes the app factory clean and lets tests import
create_app() without executing command registration side effects twice.
"""
from __future__ import annotations

import os

import click
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.article import Article
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.category import Category
from app.models.comment import Comment  # noqa: F401
from app.models.message import ContactMessage  # noqa: F401
from app.models.newsletter import NewsletterSubscriber  # noqa: F401
from app.models.page_view import PageView  # noqa: F401
from app.models.project import Project
from app.models.tag import Tag
from app.models.user import User


def _seed_admin():
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    email = os.environ.get('ADMIN_EMAIL', 'admin@datablog.local')
    password = os.environ.get('ADMIN_PASSWORD', 'admin123')

    admin = User.query.filter_by(username=username).first()
    if not admin:
        admin = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='admin',
        )
        db.session.add(admin)
        db.session.commit()
        click.echo(f'Admin user created: {username}')
    else:
        admin.role = admin.role or 'admin'
        admin.is_active = True
        db.session.commit()
        click.echo(f'Admin user already exists: {username}')
    return admin


def _seed_lookup_data():
    categories = [
        ('تحليل البيانات', 'Data Analysis', 'data-analysis'),
        ('ذكاء الأعمال', 'Business Intelligence', 'business-intelligence'),
        ('قواعد البيانات', 'Databases', 'databases'),
        ('تكامل البيانات', 'Data Integration', 'data-integration'),
    ]
    for name_ar, name_en, slug in categories:
        if not Category.query.filter_by(slug=slug).first():
            db.session.add(Category(name_ar=name_ar, name_en=name_en, slug=slug))

    tag_names = ['Power BI', 'Python', 'SQL', 'SQLite', 'Flask', 'ETL', 'Dashboard']
    for tag_name in tag_names:
        slug = tag_name.lower().replace(' ', '-')
        if not Tag.query.filter_by(slug=slug).first():
            db.session.add(Tag(name=tag_name, slug=slug))
    db.session.commit()


def _seed_sample_content(admin):
    if Article.query.first() or Project.query.first():
        click.echo('Sample articles/projects already exist. Skipping sample content.')
        return

    tag_map = {tag.name: tag for tag in Tag.query.all()}
    cat_data = Category.query.filter_by(slug='data-analysis').first()
    cat_bi = Category.query.filter_by(slug='business-intelligence').first()
    cat_db = Category.query.filter_by(slug='databases').first()
    cat_etl = Category.query.filter_by(slug='data-integration').first()

    article = Article(
        title_ar='تحليل البيانات الاستكشافي باستخدام Python',
        title_en='Exploratory Data Analysis with Python',
        slug='exploratory-data-analysis-python',
        excerpt_ar='مقال يشرح خطوات تحليل البيانات الاستكشافي وتحويل البيانات إلى مؤشرات واضحة.',
        excerpt_en='A practical article about exploratory data analysis and extracting clear indicators.',
        content_ar='هذا مثال لمحتوى مقال باللغة العربية. يمكن تعديله من لوحة التحكم.',
        content_en='This is an example English article body. You can edit it from the admin dashboard.',
        image='images/article-python.svg',
        category_id=cat_data.id if cat_data else None,
        author_id=admin.id,
        is_published=True,
    )
    article.tags = [tag_map[t] for t in ['Python', 'SQL', 'Dashboard'] if t in tag_map]
    db.session.add(article)

    article_2 = Article(
        title_ar='تصميم عملية ETL بكفاءة',
        title_en='Efficient ETL Process Design',
        slug='efficient-etl-process-design',
        excerpt_ar='شرح مبسط لتصميم عمليات استخراج وتحويل وتحميل البيانات بطريقة قابلة للصيانة.',
        excerpt_en='A simple guide to designing maintainable extraction, transformation, and loading workflows.',
        content_ar='يمكن استخدام هذا المقال لتوثيق أفضل الممارسات في تكامل البيانات وبناء مسارات ETL.',
        content_en='This article documents best practices for data integration and ETL pipelines.',
        image='images/article-etl.svg',
        category_id=cat_etl.id if cat_etl else None,
        author_id=admin.id,
        is_published=True,
    )
    article_2.tags = [tag_map[t] for t in ['ETL', 'SQL'] if t in tag_map]
    db.session.add(article_2)

    project = Project(
        title_ar='لوحة متابعة الأداء المالي',
        title_en='Financial Performance Dashboard',
        slug='financial-performance-dashboard',
        excerpt_ar='لوحة تفاعلية لمتابعة المبيعات والمصروفات وصافي الربح.',
        excerpt_en='Interactive dashboard to monitor sales, expenses, and net profit.',
        description_ar='مشروع يهدف إلى تمكين الإدارة من متابعة الأداء المالي واتخاذ قرارات مبنية على البيانات.',
        description_en='A project designed to help management track financial performance and make data-driven decisions.',
        image='images/project-dashboard.svg',
        technologies='Power BI, SQL, Python',
        demo_url='#',
        repo_url='#',
        category_id=cat_bi.id if cat_bi else None,
        is_published=True,
    )
    project.tags = [tag_map[t] for t in ['Power BI', 'SQL', 'Dashboard'] if t in tag_map]
    db.session.add(project)

    project_2 = Project(
        title_ar='مستودع بيانات للمبيعات',
        title_en='Sales Data Warehouse',
        slug='sales-data-warehouse',
        excerpt_ar='تصميم قاعدة بيانات تحليلية لتجميع بيانات المبيعات من مصادر متعددة.',
        excerpt_en='Analytical database design to consolidate sales data from multiple sources.',
        description_ar='مشروع يركز على بناء نموذج بيانات منظم يدعم التقارير ولوحات المعلومات.',
        description_en='A project focused on building a structured data model that supports reports and dashboards.',
        image='images/project-warehouse.svg',
        technologies='SQL, ETL, SQLite',
        demo_url='#',
        repo_url='#',
        category_id=cat_db.id if cat_db else None,
        is_published=True,
    )
    project_2.tags = [tag_map[t] for t in ['SQL', 'ETL', 'SQLite'] if t in tag_map]
    db.session.add(project_2)
    db.session.commit()
    click.echo('Sample articles and projects created.')


def register_commands(app):
    @app.cli.command('create-db')
    def create_db():
        """Create database tables without deleting existing data. Safe for production."""
        db.create_all()
        click.echo('Database tables created/verified successfully.')

    @app.cli.command('seed-admin')
    def seed_admin():
        """Create the admin user only if it does not exist."""
        db.create_all()
        _seed_admin()

    @app.cli.command('seed-data')
    def seed_data():
        """Create default categories, tags, admin, and sample content without deleting data."""
        db.create_all()
        admin = _seed_admin()
        _seed_lookup_data()
        _seed_sample_content(admin)
        click.echo('Seed completed successfully.')

    @app.cli.command('init-db')
    @click.option('--force', is_flag=True, help='Drop all tables before creating them. Do not use in production unless you are sure.')
    def init_db(force):
        """Initialize the database."""
        is_production = app.config.get('IS_PRODUCTION', False)
        if force:
            if is_production and not click.confirm('This is PRODUCTION. Drop all database tables?', default=False):
                click.echo('Cancelled.')
                return
            db.drop_all()
            click.echo('All tables dropped.')

        db.create_all()
        admin = _seed_admin()
        _seed_lookup_data()
        _seed_sample_content(admin)
        click.echo('Database initialized successfully.')
