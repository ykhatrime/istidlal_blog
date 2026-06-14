"""Reusable SQLAlchemy model mixins."""
from datetime import datetime

from sqlalchemy.orm import declared_attr

from app.extensions import db


class CreatedAtMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class TimestampMixin(CreatedAtMixin):
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    @declared_attr
    def deleted_at(cls):
        return db.Column(db.DateTime, nullable=True, index=True)

    @declared_attr
    def deleted_by_id(cls):
        return db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def soft_delete(self, user_id=None):
        self.deleted_at = datetime.utcnow()
        self.deleted_by_id = user_id
