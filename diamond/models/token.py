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
import hashlib

from diamond.db import db
from diamond.utils import secret

DEFAULT_DURATION = 60 * 60 * 24 # 1 day


class Token(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    digest = db.Column(db.String, nullable=False)
    payload = db.Column(db.String, nullable=False)
    nonce = db.Column(db.String, nullable=False)
    expiry = db.Column(db.DateTime, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False,
            default=datetime.datetime.utcnow)

    @classmethod
    def get(cls, user, digest):
        return Token.query \
            .filter(Token.user_id == user.id) \
            .filter(Token.digest == digest) \
            .one_or_none()

    @classmethod
    def make(cls, user, payload, duration=DEFAULT_DURATION):
        nonce = secret(size=10)
        duration = datetime.timedelta(seconds=duration)
        timestamp = datetime.datetime.utcnow()
        expiry = timestamp + duration

        token = Token(user_id=user.id, payload=payload, expiry=expiry,
                nonce=nonce, timestamp=timestamp)

        token.digest = token.make_digest(payload)

        return token

    def make_digest(self, payload):
        message = self.nonce + str(self.timestamp) + payload
        return hashlib.sha256(message) \
            .hexdigest()

    def valid(self, payload):
        expired = datetime.datetime.utcnow() > self.expiry
        invalid = self.make_digest(self.payload) != self.make_digest(payload)

        return not expired and not invalid

    def save(self):
        db.session.add(self)

        return self


db.Index('idx_token_digest_user_id', Token.digest, Token.user_id, unique=True)
