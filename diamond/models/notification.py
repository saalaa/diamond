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
from diamond.utils import cached_property
from diamond.models import Document


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    slug = db.Column(db.String, nullable=False)
    reason = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    timestamp = db.Column(db.DateTime, nullable=False,
            default=datetime.datetime.utcnow)

    user = db.relationship('User')

    @classmethod
    def get(cls, id=None, slug=None, user=None, active=None):
        query = Notification.query \
                .order_by(db.desc(Notification.timestamp))

        if id is not None:
            return query.filter(Notification.id == id) \
                    .one_or_none()

        if active is not None:
            query = query.filter(Notification.active == active)

        if slug is not None:
            query = query.filter(Notification.slug == slug)

        if user is not None:
            query = query.filter(Notification.user_id == user.id)

        if slug and user:
            return query.one_or_none()

        return query

    @classmethod
    def exists(cls, slug, user):
        return Notification.query \
                .filter(Notification.slug == slug) \
                .filter(Notification.user_id == user.id) \
                .count() != 0

    @classmethod
    def add(cls, slug, user, reason):
        if Notification.exists(slug, user):
            return

        notification = Notification(slug=slug, user_id=user.id, reason=reason)
        notification.save()

    @classmethod
    def send(cls, page, current_user):
        for notification in Notification.get(slug=page.slug, active=True):
            if notification.user == current_user:
                continue

            if not notification.user.notifications:
                continue

            notification.user.sendmail('modified', slug=page.slug)

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

    @cached_property
    def page(self):
        return Document.get(self.slug)

    def save(self):
        db.session.add(self)

        return self


db.Index('idx_notification_slug_active', Notification.slug,
        Notification.active)
db.Index('idx_notification_user_id', Notification.user_id)
db.Index('idx_notification_slug_user_id_', Notification.slug,
        Notification.user_id, unique=True)
