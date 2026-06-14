from app.extensions import db
from .mixins import SoftDeleteMixin, TimestampMixin
from .tag import article_tags


class Article(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title_ar = db.Column(db.String(220), nullable=False)
    title_en = db.Column(db.String(220), nullable=False)
    slug = db.Column(db.String(260), unique=True, nullable=False, index=True)
    excerpt_ar = db.Column(db.Text)
    excerpt_en = db.Column(db.Text)
    content_ar = db.Column(db.Text)
    content_en = db.Column(db.Text)
    image = db.Column(db.String(255))

    # SEO fields are intentionally independent from visible titles/excerpts.
    seo_title_ar = db.Column(db.String(220))
    seo_title_en = db.Column(db.String(220))
    seo_description_ar = db.Column(db.String(320))
    seo_description_en = db.Column(db.String(320))
    og_image = db.Column(db.String(255))
    canonical_url = db.Column(db.String(255))

    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False, index=True)
    views = db.Column(db.Integer, default=0, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    category = db.relationship('Category', backref='articles')
    author = db.relationship('User', foreign_keys=[author_id], backref='articles')
    deleted_by = db.relationship('User', foreign_keys='Article.deleted_by_id')
    tags = db.relationship('Tag', secondary=article_tags, backref='articles')

    def title(self, lang='ar'):
        return self.title_ar if lang == 'ar' else self.title_en

    def excerpt(self, lang='ar'):
        return self.excerpt_ar if lang == 'ar' else self.excerpt_en

    def content(self, lang='ar'):
        return self.content_ar if lang == 'ar' else self.content_en

    def seo_title(self, lang='ar'):
        value = self.seo_title_ar if lang == 'ar' else self.seo_title_en
        return value or self.title(lang)

    def seo_description(self, lang='ar'):
        value = self.seo_description_ar if lang == 'ar' else self.seo_description_en
        return value or self.excerpt(lang)

    def open_graph_image(self):
        return self.og_image or self.image

    def soft_delete(self, user_id=None):
        super().soft_delete(user_id)
        self.is_published = False
