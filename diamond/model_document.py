import datetime

from diamond.db import db
from diamond.utils import cached_property
from diamond.model_metadata import Metadata

DEFAULT_BODY = '# %(name)s\n\nDescribe [[%(name)s]] here.'

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_slug = db.Column(db.String, db.ForeignKey('users.slug'))
    mtime = db.Column(db.DateTime, nullable=False,
            default=datetime.datetime.utcnow)
    comment = db.Column(db.Text)
    active = db.Column(db.Boolean, nullable=False, default=0)

    user = db.relationship('User')

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
        return Document.query \
                .filter(Document.active == True) \
                .count()

    @classmethod
    def get(cls, name, version=None):
        if version:
            return Document.query \
                    .filter(Document.id == version) \
                    .filter(Document.name == name) \
                    .one_or_none()

        item = Document.query \
                .filter(Document.active == True) \
                .filter(Document.name == name) \
                .one_or_none()

        if not item:
            item = Document(name=name, body=DEFAULT_BODY % {
                'name': name.replace('_', ' ')})

        return item

    @classmethod
    def changes(cls):
        return Document.query \
                .order_by(db.desc(Document.mtime)) \
                .limit(100)

    @classmethod
    def titles(cls):
        return Document.query \
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

        items = Document.query \
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

        items = db.session.query(Metadata.key, Metadata.value, db.func.count()) \
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
        db.session.add(item)

    def save(self):
        Document.deactivate(self.name)
        Metadata.deactivate(self.name)

        self.active = True
        db.session.add(self)

    def history(self):
        return Document.query \
                .filter(Document.name == self.name) \
                .order_by(db.desc(Document.mtime)) \
                .limit(100)
