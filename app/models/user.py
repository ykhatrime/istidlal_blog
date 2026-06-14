from datetime import datetime

from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    ROLE_ADMIN = 'admin'
    ROLE_EDITOR = 'editor'
    ROLE_MODERATOR = 'moderator'
    ROLE_VIEWER = 'viewer'
    VALID_ROLES = {ROLE_ADMIN, ROLE_EDITOR, ROLE_MODERATOR, ROLE_VIEWER}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), default=ROLE_ADMIN, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_role(self, role):
        self.role = role if role in self.VALID_ROLES else self.ROLE_VIEWER

    @property
    def display_role(self):
        return self.role or self.ROLE_VIEWER
