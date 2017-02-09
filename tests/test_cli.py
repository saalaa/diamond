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

from diamond.models import Document
from diamond.redis import redis
from diamond.db import db
from diamond.cli import load_fixtures


def test_drop_db():
    db.create_all()
    db.drop_all()

    inspector = db.inspect(db.engine)
    names = inspector.get_table_names()

    # If the database was created through Alembic migrations, the marker table
    # is never removed by SQLAlchemy.

    if 'alembic_version' in names:
        assert len(names) == 1
    else:
        assert len(names) == 0


def test_init_db():
    db.drop_all()
    db.create_all()

    inspector = db.inspect(db.engine)
    names = inspector.get_table_names()

    # If the database was created through Alembic migrations, the marker table
    # is never removed by SQLAlchemy.

    if 'alembic_version' in names:
        assert len(names) == 7
    else:
        assert len(names) == 6


def test_clear_cache():
    redis.set('xxx', 42)
    redis.flushdb()

    assert redis.get('xxx') is None


def test_load_fixtures():
    db.create_all()

    load_fixtures()

    assert Document.count() == 3
