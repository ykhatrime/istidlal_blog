from app.extensions import db
from .mixins import CreatedAtMixin


class PageView(CreatedAtMixin, db.Model):
    """Privacy-aware internal page-view analytics.

    The model never stores a raw IP address or the raw visitor cookie value.
    `visitor_hash` is an HMAC of the browser cookie, while `ip_hash` is an
    HMAC of the request IP for fallback/debugging without exposing the IP.
    """

    __tablename__ = 'page_views'
    __table_args__ = (
        db.Index('ix_page_views_created_path', 'created_at', 'path'),
        db.Index('ix_page_views_page_lookup', 'page_type', 'page_id'),
        db.Index('ix_page_views_visitor_created', 'visitor_hash', 'created_at'),
    )

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(500), nullable=False, index=True)
    endpoint = db.Column(db.String(120), nullable=True, index=True)
    page_type = db.Column(db.String(40), nullable=False, default='page', index=True)
    page_id = db.Column(db.Integer, nullable=True, index=True)
    page_title = db.Column(db.String(255), nullable=True)
    visitor_hash = db.Column(db.String(64), nullable=False, index=True)
    ip_hash = db.Column(db.String(64), nullable=True, index=True)
    user_agent = db.Column(db.String(255), nullable=True)
    referrer = db.Column(db.String(500), nullable=True)
    language = db.Column(db.String(5), nullable=True, index=True)
    status_code = db.Column(db.Integer, nullable=False, default=200)

    def display_title(self):
        return self.page_title or self.path
