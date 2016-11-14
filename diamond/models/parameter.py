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

import time

from diamond.db import db

CACHE_DELAY = 300 # 5 minutes

def param(key, default='', cast=None):
    return Parameter.get(key, default, cast)

class Parameter(db.Model):
    __tablename__ = 'parameters'

    key = db.Column(db.String, primary_key=True)
    value = db.Column(db.String, nullable=False)

    cache = timestamp = None

    @classmethod
    def get_all(cls):
        items = Parameter.query \
                .all()

        values = {}
        for item in items:
            values[item.key] = item.value

        return values

    @classmethod
    def get(cls, key, default='', cast=None):
        now = time.time()

        if not cls.cache or cls.timestamp + CACHE_DELAY > now:
            cls.cache = cls.get_all()
            cls.timestamp = now

        value = cls.cache.get(key, default)

        if cast:
            value = cast(value)

        return value

    @classmethod
    def clear_cache(cls):
        cls.cache = cls.timestamp = None

    @classmethod
    def set(cls, key, value):
        items = Parameter.query \
                .filter(Parameter.key == key)

        for item in items:
            db.session.delete(item)

        Parameter(key=key, value=value) \
                .save()

    def save(self):
        db.session.add(self)

db.Index('idx_parameter_key', Parameter.key)
