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
from diamond.cli import drop_db, init_db
from diamond.models import Document, User


@pytest.fixture
def database():
    drop_db()
    init_db()


def test_all(database):
    assert not User.exists('a')
    assert not User.exists('b')
    assert not User.exists('c')
    assert not User.exists('d')

    assert User.is_first()

    User(slug='a', admin=True).save()

    db.session.commit()

    assert not User.is_first()

    User(slug='b', admin=False).save()
    User(slug='c', admin=False).save()
    User(slug='d', admin=False).save()

    Document(body='', slug='b', title='B').save()
    Document(body='', slug='c', title='C').save()

    db.session.commit()

    assert User.exists('a')
    assert User.exists('b')
    assert User.exists('c')
    assert User.exists('d')

    assert User.get('a').name == 'a'
    assert User.get('b').name == 'B'
    assert User.get('c').name == 'C'
    assert User.get('d').name == 'd'

    assert not User.get('e')

    user = User.get('a') \
            .set_password('hello123') \
            .save()

    db.session.commit()

    assert user.get_id() == 'a'

    assert user.check_password('hello123')
