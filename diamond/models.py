import datetime
import bcrypt
import time

from flask_login import UserMixin

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, \
        ForeignKey, create_engine, desc, func

from utils import cached_property
from app import app

PARAMETER_DELAY = 300
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

def param(key, default='', cast=None):
    return Parameter.get(key, default, cast)

class Parameter(Base):
    __tablename__ = 'parameters'

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)

    cache = timestamp = None

    @classmethod
    def get_all(cls):
        items = db.query(Parameter) \
                .all()

        values = {}
        for item in items:
            values[item.key] = item.value

        return values

    @classmethod
    def get(cls, key, default='', cast=None):
        now = time.time()

        if not cls.cache or cls.timestamp + PARAMETER_DELAY > now:
            cls.cache = cls.get_all()
            cls.timestamp = now

        value = cls.cache.get(key, default)

        if cast:
            value = cast(value)

        return value

    @classmethod
    def clear_cache(cls):
        cls.cache = None

    @classmethod
    def set(cls, key, value):
        items = db.query(Parameter) \
                .filter(Parameter.key == key) \
                .all()

        for item in items:
            db.delete(item)

        Parameter(key=key, value=value) \
                .save()

    def save(self):
        db.add(self)

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

    def save(self):
        db.add(self)

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
        return self.title[0].lower() if self.title else self.slug[0]

    @cached_property
    def ymd(self):
        return self.mtime.strftime('%Y-%m-%d') if self.mtime else None

    @property
    def hm(self):
        return self.mtime.strftime('%H:%M') if self.mtime else None

    @property
    def ymd_hm(self):
        return self.mtime.strftime('%Y-%m-%d %H:%M') if self.mtime else None

    @cached_property
    def meta(self):
        return Metadata.get(self.name)

    @classmethod
    def count(cls):
        return db.query(Document) \
                .filter(Document.active == True) \
                .count()

    @classmethod
    def get(cls, name, version=None):
        if version:
            return db.query(Document) \
                    .filter(Document.id == version) \
                    .filter(Document.name == name) \
                    .one_or_none()

        item = db.query(Document) \
                .filter(Document.active == True) \
                .filter(Document.name == name) \
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
    def search(cls, query=None, filters=None):
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
            items = items.filter(Document.body.like('%' + query + '%'))

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
    def deactivate(cls, name):
        item = Document.get(name)

        if not item.id:
            return

        item.active = False
        db.add(item)

    def save(self):
        Document.deactivate(self.name)
        Metadata.deactivate(self.name)

        self.active = True
        db.add(self)

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
    def deactivate(cls, name):
        for item in Metadata.get(name):
            db.delete(item)

    def save(self):
        db.add(self)

Base.metadata.create_all(Engine, checkfirst=True)
