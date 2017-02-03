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
import six

from flask import request
from flask_login import UserMixin
from slugify import slugify


from diamond import tasks
from diamond.utils import cached_property, make_context
from diamond.db import db
from diamond.models.document import Document


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    validated = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    notifications = db.Column(db.Boolean, nullable=False, default=True)
    timestamp = db.Column(db.DateTime, nullable=False,
            default=datetime.datetime.utcnow)

    @cached_property
    def document(self):
        return Document.get(slugify(self.name))

    @classmethod
    def is_first(self):
        return User.query.count() == 0

    @classmethod
    def exists(self, email=None, name=None):
        if email is not None:
            return User.query.filter(User.email == email) \
                    .count() != 0

        if name is not None:
            return User.query.filter(User.name == name) \
                    .count() != 0

        return True

    @classmethod
    def get(cls, email=None, id=None):
        if email:
            return User.query.filter(User.email == email) \
                    .one_or_none()
        else:
            return User.query.filter(User.id == id) \
                    .one_or_none()

    def get_id(self):
        return self.id

    def set_password(self, password):
        if isinstance(password, six.text_type):
            password = password.encode('utf-8')

        self.password = bcrypt.hashpw(password, bcrypt.gensalt())

        return self

    def check_password(self, password):
        self_password = self.password

        if isinstance(password, six.text_type):
            password = password.encode('utf-8')

        if isinstance(self_password, six.text_type):
            self_password = self_password.encode('utf-8')

        return bcrypt.checkpw(password, self_password)

    def sendmail(self, template, **kwargs):
        context = make_context(request, self)
        sendmail = getattr(tasks, 'send_' + template)

        if tasks.with_celery():
            sendmail = sendmail.delay

        sendmail(context, **kwargs)

    def save(self):
        db.session.add(self)

        return self


db.Index('idx_user_email', User.email, unique=True)
db.Index('idx_user_name', User.name, unique=True)
