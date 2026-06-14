from datetime import datetime
from app.extensions import db

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(120), nullable=False)
    name_en = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(160), unique=True, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(30), default='#2563eb')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def name(self, lang='ar'):
        return self.name_ar if lang == 'ar' else self.name_en
