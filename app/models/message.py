from app.extensions import db
from .mixins import CreatedAtMixin, SoftDeleteMixin


class ContactMessage(CreatedAtMixin, SoftDeleteMixin, db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(180), nullable=False)
    subject = db.Column(db.String(220))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    ip_address = db.Column(db.String(80), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)

