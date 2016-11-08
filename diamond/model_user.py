import datetime
import bcrypt

from flask_login import UserMixin
from diamond.utils import cached_property
from diamond.db import db
from diamond.model_document import Document

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    slug = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    admin = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False,
            default=datetime.datetime.utcnow)

    @cached_property
    def document(self):
        return Document.get(self.slug)

    @cached_property
    def name(self):
        return self.document.title if self.document else self.slug

    @classmethod
    def is_first(self):
        return User.query.count() == 0

    @classmethod
    def exists(self, slug):
        return User.query \
                .filter(User.slug == slug) \
                .count() != 0

    @classmethod
    def get(cls, slug):
        return User.query \
                .filter(User.slug == slug) \
                .one_or_none()

    def get_id(self):
        return self.slug

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf8'),
                bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf8'),
                self.password.encode('utf8'))

    def save(self):
        db.session.add(self)
