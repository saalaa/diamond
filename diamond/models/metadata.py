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

from diamond.db import db


class Metadata(db.Model):
    __tablename__ = 'metadata'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, nullable=False) # ForeignKey('documents.slug')
    key = db.Column(db.String, nullable=False)
    value = db.Column(db.String, nullable=False)

    structural_keys = ('previous', 'next', 'type')

    @classmethod
    def get(cls, slug, key=None, ignores=None, structural=True):
        items = Metadata.query \
                .filter(Metadata.slug == slug) \

        if key:
            items = items.filter(Metadata.key == key) \
                    .all()

            return [item.value for item in items]

        if ignores:
            items = items.filter(Metadata.key.notin_(ignores))

        if not structural:
            items = items.filter(Metadata.key.notin_(Metadata.structural_keys))

        return items.order_by(Metadata.key, Metadata.value) \
                .all()

    @classmethod
    def search(cls, key, value):
        items = db.session.query(Metadata.slug) \
                .filter(Metadata.key == key) \
                .filter(Metadata.value == value) \
                .order_by(Metadata.key, Metadata.value)

        return set([item[0] for item in items])

    @classmethod
    def deactivate(cls, slug):
        for item in Metadata.get(slug):
            db.session.delete(item)

    def save(self):
        db.session.add(self)

        return self


db.Index('idx_metadata_slug', Metadata.slug)
db.Index('idx_metadata_key_value', Metadata.key, Metadata.value)
