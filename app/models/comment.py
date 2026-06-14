from app.extensions import db
from .mixins import SoftDeleteMixin, TimestampMixin


class Comment(TimestampMixin, SoftDeleteMixin, db.Model):
    """Private comment submitted from article/project pages and managed only in admin."""

    __tablename__ = 'comments'

    STATUS_NEW = 'new'
    STATUS_READ = 'read'
    STATUS_ARCHIVED = 'archived'
    STATUS_SPAM = 'spam'
    VALID_STATUSES = {STATUS_NEW, STATUS_READ, STATUS_ARCHIVED, STATUS_SPAM}

    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String(20), nullable=False, index=True)  # article / project
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id', ondelete='SET NULL'), nullable=True, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True, index=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), nullable=True)
    comment = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default=STATUS_NEW, nullable=False, index=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)  # legacy compatibility
    ip_address = db.Column(db.String(80), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    internal_note = db.Column(db.Text, nullable=True)

    article = db.relationship('Article', backref=db.backref('comments', lazy='dynamic'))
    project = db.relationship('Project', backref=db.backref('comments', lazy='dynamic'))
    deleted_by = db.relationship('User', foreign_keys='Comment.deleted_by_id')

    @property
    def content_item(self):
        return self.article if self.content_type == 'article' else self.project

    def content_title(self, lang='ar'):
        item = self.content_item
        return item.title(lang) if item else ('محذوف' if lang == 'ar' else 'Deleted')

    def set_status(self, status):
        if status not in self.VALID_STATUSES:
            status = self.STATUS_NEW
        self.status = status
        self.is_read = status in {self.STATUS_READ, self.STATUS_ARCHIVED, self.STATUS_SPAM}

    def soft_delete(self, user_id=None):
        super().soft_delete(user_id)
        self.set_status(self.STATUS_ARCHIVED)
