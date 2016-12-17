# Copyright (C) 1999, 2000 Martin Pool <mbp@humbug.org.au>
# Copyright (C) 2003 Kimberley Burchett <http://www.kimbly.com>
# Copyright (C) 2016 Benoit Myard <myardbenoit@gmail.com>
#
# This file is part of Diamond wiki.
#
# Diamond wiki is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Diamond wiki is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Diamond wiki. If not, see <http://www.gnu.org/licenses/>.

import datetime

from diamond.db import db
from diamond.utils import cached_property, memoized
from diamond.models.metadata import Metadata

DEFAULT_BODY = '# %(slug)s\n\nDescribe [[%(slug)s]] here.'


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String, db.ForeignKey('users.slug'))
    comment = db.Column(db.Text)
    active = db.Column(db.Boolean, nullable=False, default=0)
    timestamp = db.Column(db.DateTime, nullable=False,
            default=datetime.datetime.utcnow)

    user = db.relationship('User')

    @property
    def initial(self):
        return self.title[0].lower() if self.title else self.slug[0]

    @cached_property
    def ymd(self):
        return self.timestamp.strftime('%Y-%m-%d') if self.timestamp else None

    @cached_property
    def hm(self):
        return self.timestamp.strftime('%H:%M') if self.timestamp else None

    @cached_property
    def ymd_hm(self):
        return self.timestamp.strftime('%Y-%m-%d %H:%M') if self.timestamp \
                else None

    @memoized
    def meta(self, key=None, ignores=None, structural=True):
        return Metadata.get(self.slug, key, ignores, structural)

    @memoized
    def keys(self, ignores=None, structural=True):
        return set([item.key for item in
            self.meta(ignores=ignores, structural=structural)])

    @classmethod
    def count(cls):
        return Document.query \
                .filter(Document.active == True) \
                .count()

    @classmethod
    def get(cls, slug, version=None):
        if version:
            return Document.query \
                    .filter(Document.id == version) \
                    .filter(Document.slug == slug) \
                    .one_or_none()

        item = Document.query \
                .filter(Document.active == True) \
                .filter(Document.slug == slug) \
                .one_or_none()

        if not item:
            item = Document(slug=slug, body=DEFAULT_BODY % {
                'slug': slug.replace('_', ' ')})

        return item

    @classmethod
    def changes(cls):
        return Document.query \
                .order_by(db.desc(Document.timestamp))

    @classmethod
    def titles(cls):
        return Document.query \
                .filter(Document.active == True) \
                .order_by(Document.title)

    @classmethod
    def search(cls, query=None, filters=None):
        slugs = None
        if filters:
            filters = [Metadata.search(key, value) for key, value in filters]

            slugs = None
            for filter in filters:
                if slugs is None:
                    slugs = filter
                else:
                    slugs = slugs.intersection(filter)

        items = Document.query \
                .filter(Document.active == True) \
                .order_by(Document.slug)

        if slugs is not None:
            items = items.filter(Document.slug.in_(slugs))

        if query:
            items = items.filter(Document.body.like('%' + query + '%'))

        return items.all()

    @classmethod
    def facets(cls, pages, ignores=None, all=False):
        if not pages:
            return {}

        ignores = ignores or []
        ignores.extend(Metadata.structural_keys)

        slugs = [page.slug for page in pages]

        count = db.func.count
        items = db.session.query(Metadata.key, Metadata.value, count()) \
                .filter(Metadata.slug.in_(slugs)) \
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
    def deactivate(cls, slug):
        item = Document.get(slug)

        if not item.id:
            return

        item.active = False
        db.session.add(item)

    def save(self):
        self.active = True
        db.session.add(self)

        return self

    def history(self):
        return Document.query \
                .filter(Document.slug == self.slug) \
                .order_by(db.desc(Document.timestamp))


db.Index('idx_document_slug', Document.slug)
db.Index('idx_document_active', Document.active)
db.Index('idx_document_slug_active', Document.slug, Document.active)
