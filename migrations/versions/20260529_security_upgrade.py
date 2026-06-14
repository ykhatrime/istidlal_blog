"""security, seo, soft-delete, comments status, audit log

Revision ID: 20260529_security_upgrade
Revises:
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = '20260529_security_upgrade'
down_revision = None
branch_labels = None
depends_on = None


def _columns(table_name):
    bind = op.get_bind()
    return {col['name'] for col in inspect(bind).get_columns(table_name)}


def _tables():
    bind = op.get_bind()
    return set(inspect(bind).get_table_names())


def _add_column_if_missing(table_name, column):
    if table_name in _tables() and column.name not in _columns(table_name):
        op.add_column(table_name, column)


def upgrade():
    if 'audit_logs' not in _tables():
        op.create_table(
            'audit_logs',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('action', sa.String(length=80), nullable=False),
            sa.Column('entity_type', sa.String(length=80), nullable=True),
            sa.Column('entity_id', sa.Integer(), nullable=True),
            sa.Column('details', sa.Text(), nullable=True),
            sa.Column('ip_address', sa.String(length=80), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
        )
        op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
        op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
        op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])
        op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
        op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])

    for table in ['articles', 'projects']:
        _add_column_if_missing(table, sa.Column('seo_title_ar', sa.String(length=220), nullable=True))
        _add_column_if_missing(table, sa.Column('seo_title_en', sa.String(length=220), nullable=True))
        _add_column_if_missing(table, sa.Column('seo_description_ar', sa.String(length=320), nullable=True))
        _add_column_if_missing(table, sa.Column('seo_description_en', sa.String(length=320), nullable=True))
        _add_column_if_missing(table, sa.Column('og_image', sa.String(length=255), nullable=True))
        _add_column_if_missing(table, sa.Column('canonical_url', sa.String(length=255), nullable=True))
        _add_column_if_missing(table, sa.Column('deleted_at', sa.DateTime(), nullable=True))
        _add_column_if_missing(table, sa.Column('deleted_by_id', sa.Integer(), nullable=True))

    _add_column_if_missing('articles', sa.Column('is_featured', sa.Boolean(), nullable=False, server_default=sa.false()))

    _add_column_if_missing('comments', sa.Column('status', sa.String(length=20), nullable=False, server_default='new'))
    _add_column_if_missing('comments', sa.Column('ip_address', sa.String(length=80), nullable=True))
    _add_column_if_missing('comments', sa.Column('user_agent', sa.String(length=255), nullable=True))
    _add_column_if_missing('comments', sa.Column('internal_note', sa.Text(), nullable=True))
    _add_column_if_missing('comments', sa.Column('updated_at', sa.DateTime(), nullable=True))
    _add_column_if_missing('comments', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    _add_column_if_missing('comments', sa.Column('deleted_by_id', sa.Integer(), nullable=True))

    _add_column_if_missing('messages', sa.Column('ip_address', sa.String(length=80), nullable=True))
    _add_column_if_missing('messages', sa.Column('user_agent', sa.String(length=255), nullable=True))
    _add_column_if_missing('messages', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    _add_column_if_missing('messages', sa.Column('deleted_by_id', sa.Integer(), nullable=True))

    _add_column_if_missing('newsletter_subscribers', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    _add_column_if_missing('newsletter_subscribers', sa.Column('deleted_by_id', sa.Integer(), nullable=True))

    _add_column_if_missing('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
    _add_column_if_missing('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))

    bind = op.get_bind()
    if 'comments' in _tables():
        bind.execute(sa.text("UPDATE comments SET status = CASE WHEN is_read = 1 THEN 'read' ELSE 'new' END WHERE status IS NULL OR status = ''"))


def downgrade():
    # Conservative downgrade: keep data-bearing columns except audit_logs.
    if 'audit_logs' in _tables():
        op.drop_table('audit_logs')
