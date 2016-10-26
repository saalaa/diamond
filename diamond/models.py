import datetime
import bcrypt

from flask_login import UserMixin

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, \
        ForeignKey, create_engine, desc, func

from .utils import cached_property
from .app import app

DEFAULT_BODY = '# %(name)s\n\nDescribe [[%(name)s]] here.'

Base = declarative_base()

Engine = create_engine(app.config['DATABASE_URL'], convert_unicode=True,
        echo=app.config['SQL_DEBUG'])

Session = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

db = scoped_session(Session)

def db_init():
    Base.metadata.create_all(Engine, checkfirst=True)

def db_drop():
    Base.metadata.drop_all(Engine, checkfirst=True)

class User(UserMixin, Base):
    __tablename__ = 'users'

    slug = Column(String, primary_key=True)
    password = Column(String)
    admin = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, nullable=False,
            default=datetime.datetime.utcnow)

    @cached_property
    def document(self):
        return Document.get(self.slug)

    @cached_property
    def name(self):
        return self.document.title if self.document else self.slug

    @classmethod
    def is_first(self):
        return db.query(User) \
                .count() == 0

    @classmethod
    def exists(self, slug):
        return db.query(User) \
                .filter(User.slug == slug) \
                .count() != 0

    @classmethod
    def get(cls, slug):
        return db.query(User) \
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

    def save(self, commit=True):
        db.add(self)

        if commit:
            db.commit()

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    user_slug = Column(String, ForeignKey('users.slug'))
    mtime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    comment = Column(Text)
    active = Column(Boolean, nullable=False, default=0)

    user = relationship('User')

    @property
    def initial(self):
        return self.title[0].lower()

    @cached_property
    def ymd(self):
        return self.mtime.strftime('%Y-%m-%d')

    @property
    def hm(self):
        return self.mtime.strftime('%H:%M')

    @property
    def ymd_hm(self):
        return self.mtime.strftime('%Y-%m-%d %H:%M') if self.mtime else 'never'

    @cached_property
    def meta(self):
        return Metadata.get(self.name)

    @classmethod
    def count(cls):
        return db.query(Document) \
                .filter(Document.active == True) \
                .count()

    @classmethod
    def get(cls, name):
        item = db.query(Document) \
                .filter(Document.name == name) \
                .filter(Document.active == True) \
                .one_or_none()

        if not item:
            item = Document(name=name, body=DEFAULT_BODY % {
                'name': name.replace('_', ' ')})

        return item

    @classmethod
    def changes(cls):
        return db.query(Document) \
                .order_by(desc(Document.mtime)) \
                .limit(100)

    @classmethod
    def titles(cls):
        return db.query(Document) \
                .filter(Document.active == True) \
                .order_by(Document.title) \
                .all()

    @classmethod
    def search(cls, query, fulltext, filters=None):
        names = None
        if filters:
            filters = [Metadata.search(key, value) for key, value in filters]
            names = reduce(lambda acc, x: acc if acc is None else \
                    acc.intersection(x), filters)

        items = db.query(Document) \
                .filter(Document.active == True) \
                .order_by(Document.name)

        if names is not None:
            items = items.filter(Document.name.in_(names))

        if query:
            if fulltext:
                items = items.filter(Document.body.like('%' + query + '%'))
            else:
                items = items.filter(Document.name.like('%' + query + '%'))

        return items.all()

    @classmethod
    def facets(cls, pages, ignores=None, all=False):
        ignores = ignores or []

        names = [page.name for page in pages]

        items = db.query(Metadata.key, Metadata.value, func.count()) \
                .filter(Metadata.name.in_(names)) \
                .group_by(Metadata.key, Metadata.value) \
                .order_by(Metadata.key, Metadata.value)

        facets = {}
        for item in items:
            if item[0] in ignores:
                continue

            facets.setdefault(item[0], []) \
                    .append((item[1], item[2]))

        return facets

    @classmethod
    def deactivate(cls, name, commit=True):
        item = Document.get(name)

        if not item.id:
            return

        item.active = False
        db.add(item)

        if commit:
            db.commit()

    def save(self, commit=True):
        Document.deactivate(self.name, False)
        Metadata.deactivate(self.name, False)

        self.active = True
        db.add(self)

        if commit:
            db.commit()

    def history(self):
        return db.query(Document) \
                .filter(Document.name == self.name) \
                .order_by(desc(Document.mtime)) \
                .limit(100)

class Metadata(Base):
    __tablename__ = 'metadata'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

    @classmethod
    def get(self, name):
        return db.query(Metadata) \
                .filter(Metadata.name == name) \
                .order_by(Metadata.key, Metadata.value) \
                .all()

    @classmethod
    def search(self, key, value):
        items = db.query(Metadata.name) \
                .filter(Metadata.key == key) \
                .filter(Metadata.value == value) \
                .order_by(Metadata.key, Metadata.value)

        return set([item[0] for item in items])

    @classmethod
    def deactivate(cls, name, commit=True):
        for item in Metadata.get(name):
            db.delete(item)

        if commit:
            db.commit()

    def save(self, commit=True):
        db.add(self)

        if commit:
            db.commit()

Base.metadata.create_all(Engine, checkfirst=True)
