from app.extensions import db
from .mixins import CreatedAtMixin, SoftDeleteMixin


class NewsletterSubscriber(CreatedAtMixin, SoftDeleteMixin, db.Model):
    __tablename__ = 'newsletter_subscribers'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(180), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def soft_delete(self, user_id=None):
        super().soft_delete(user_id)
        self.is_active = False
