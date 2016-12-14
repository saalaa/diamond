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
from diamond.models import Document
from diamond.redis import redis
from diamond.cli import drop_db, init_db, clear_cache, load_fixtures


def test_drop_db():
    init_db()
    drop_db()

    inspector = db.inspect(db.engine)
    names = inspector.get_table_names()

    assert len(names) == 0


def test_init_db():
    drop_db()
    init_db()

    inspector = db.inspect(db.engine)
    names = inspector.get_table_names()

    assert len(names) == 4


def test_clear_cache():
    redis.set('xxx', 42)

    clear_cache()

    assert redis.get('xxx') is None


def test_load_fixtures():
    init_db()

    load_fixtures()

    assert Document.count() == 15
