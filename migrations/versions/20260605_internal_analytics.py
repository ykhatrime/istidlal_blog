"""internal visitor analytics

Revision ID: 20260605_internal_analytics
Revises: 20260529_security_upgrade
Create Date: 2026-06-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = '20260605_internal_analytics'
down_revision = '20260529_security_upgrade'
branch_labels = None
depends_on = None


def _tables():
    bind = op.get_bind()
    return set(inspect(bind).get_table_names())


def _create_index_if_missing(index_name, table_name, columns):
    bind = op.get_bind()
    existing = {idx['name'] for idx in inspect(bind).get_indexes(table_name)} if table_name in _tables() else set()
    if index_name not in existing:
        op.create_index(index_name, table_name, columns)


def upgrade():
    if 'page_views' not in _tables():
        op.create_table(
            'page_views',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('path', sa.String(length=500), nullable=False),
            sa.Column('endpoint', sa.String(length=120), nullable=True),
            sa.Column('page_type', sa.String(length=40), nullable=False, server_default='page'),
            sa.Column('page_id', sa.Integer(), nullable=True),
            sa.Column('page_title', sa.String(length=255), nullable=True),
            sa.Column('visitor_hash', sa.String(length=64), nullable=False),
            sa.Column('ip_hash', sa.String(length=64), nullable=True),
            sa.Column('user_agent', sa.String(length=255), nullable=True),
            sa.Column('referrer', sa.String(length=500), nullable=True),
            sa.Column('language', sa.String(length=5), nullable=True),
            sa.Column('status_code', sa.Integer(), nullable=False, server_default='200'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
        )
    _create_index_if_missing('ix_page_views_path', 'page_views', ['path'])
    _create_index_if_missing('ix_page_views_endpoint', 'page_views', ['endpoint'])
    _create_index_if_missing('ix_page_views_page_type', 'page_views', ['page_type'])
    _create_index_if_missing('ix_page_views_page_id', 'page_views', ['page_id'])
    _create_index_if_missing('ix_page_views_visitor_hash', 'page_views', ['visitor_hash'])
    _create_index_if_missing('ix_page_views_ip_hash', 'page_views', ['ip_hash'])
    _create_index_if_missing('ix_page_views_language', 'page_views', ['language'])
    _create_index_if_missing('ix_page_views_created_at', 'page_views', ['created_at'])
    _create_index_if_missing('ix_page_views_created_path', 'page_views', ['created_at', 'path'])
    _create_index_if_missing('ix_page_views_page_lookup', 'page_views', ['page_type', 'page_id'])
    _create_index_if_missing('ix_page_views_visitor_created', 'page_views', ['visitor_hash', 'created_at'])


def downgrade():
    if 'page_views' in _tables():
        op.drop_table('page_views')
