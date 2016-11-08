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
import bcrypt

from flask_login import UserMixin
from diamond.utils import cached_property
from diamond.db import db
from diamond.models.document import Document

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
