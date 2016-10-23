import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, \
        desc, func

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

from .app import app

Base = declarative_base()

Engine = create_engine(app.config['DATABASE_URL'], convert_unicode=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

db = scoped_session(Session)

def db_init():
    Base.metadata.create_all(Engine, checkfirst=True)

def db_drop():
    Base.metadata.drop_all(Engine, checkfirst=True)

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    mtime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    active = Column(Boolean, nullable=False, default=0)

    @property
    def meta(self):
        return Metadata.get(self.name)

    @classmethod
    def count(cls):
        return db.query(Document) \
                .filter(Document.active == True) \
                .count()

    @classmethod
    def get(cls, name):
        document = db.query(Document) \
                .filter(Document.name == name) \
                .filter(Document.active == True) \
                .one_or_none()

        if not document:
            document = Document(name=name, body='Describe [[%s]] here.' %
                    name.replace('_', ' '))

        return document

    @classmethod
    def changes(cls):
        return db.query(Document) \
                .order_by(desc(Document.mtime)) \
                .limit(100)

    @classmethod
    def titles(cls):
        items = db.query(Document) \
                .filter(Document.active == True) \
                .order_by(Document.name)

        return [item.name for item in items]

    @classmethod
    def search(cls, query, fulltext, filters=None):
        names = None
        if filters:
            filters = [Metadata.search(key, value) for key, value in filters]
            names = reduce(lambda acc, x: acc if acc is None else \
                    acc.intersection(x), filters)

        items = db.query(Document.name) \
                .filter(Document.active == True) \
                .order_by(Document.name)

        if names is not None:
            items = items.filter(Document.name.in_(names))

        if query:
            if fulltext:
                items = items.filter(Document.body.like('%' + query + '%'))
            else:
                items = items.filter(Document.name.like('%' + query + '%'))

        return [item[0] for item in items]

    @classmethod
    def facets(cls, names, ignores=None, all=False):
        ignores = ignores or []

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
                .order_by(Metadata.key, Metadata.value)

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
