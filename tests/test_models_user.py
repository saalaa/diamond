# coding=utf-8

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

import pytest

from diamond.db import db
from diamond.models import User


def test_all(client):
    assert not User.exists(email='a@a.a')
    assert not User.exists(email='b@b.b')
    assert not User.exists(email='c@c.c')
    assert not User.exists(email='d@d.d')

    assert not User.exists(name='a')
    assert not User.exists(name='b')
    assert not User.exists(name='c')
    assert not User.exists(name='d')

    assert User.is_first()

    user = User(email='a@a.a', name='a', password='').save()

    db.session.commit()

    assert not user.admin

    assert not User.is_first()

    User(email='b@b.b', name='B', password='').save()
    User(email='c@c.c', name='C', password='').save()
    User(email='d@d.d', name='D', password='').save()

    db.session.commit()

    assert User.exists(email='a@a.a')
    assert User.exists(email='b@b.b')
    assert User.exists(email='c@c.c')
    assert User.exists(email='d@d.d')

    assert User.exists(name='a')
    assert User.exists(name='B')
    assert User.exists(name='C')
    assert User.exists(name='D')

    assert User.get('a@a.a').name == 'a'
    assert User.get('b@b.b').name == 'B'
    assert User.get('c@c.c').name == 'C'
    assert User.get('d@d.d').name == 'D'

    assert not User.get('e@e.e')


def test_u_string(client):
    user = User(email='u-string@example.com', name='u-string') \
            .set_password(u'é') \
            .save()

    db.session.commit()

    user = User.get('u-string@example.com')

    assert user.check_password('é')
    assert user.check_password(u'é')
    assert user.check_password(b'\xc3\xa9')

def test_b_string(client):
    user = User(email='b-string@example.com', name='b-string') \
            .set_password(b'\xc3\xa9') \
            .save()

    db.session.commit()

    user = User.get('b-string@example.com')

    assert user.check_password('é')
    assert user.check_password(u'é')
    assert user.check_password(b'\xc3\xa9')


def test_string(client):
    user = User(email='string@example.com', name='string') \
            .set_password('é') \
            .save()

    db.session.commit()

    user = User.get('string@example.com')

    assert user.check_password('é')
    assert user.check_password(u'é')
    assert user.check_password(b'\xc3\xa9')
