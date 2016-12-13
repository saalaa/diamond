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

from flask import request
from diamond.cli import init_db, drop_db, clear_cache
from diamond.caching import cached_body, invalidator
from diamond.models import Document
from diamond.redis import redis
from diamond.app import app
from diamond.db import db

@pytest.fixture
def database():
    drop_db()
    init_db()

    clear_cache()

def test_cached_body(database):
    data = cached_body(Document(slug='a', title='A', body='xxx', active=False),
            'cache-')

    assert 'xxx' in data
    assert not redis.get('cache-a')

    data = cached_body(Document(slug='b', title='B', body='xxx', active=True),
            'cache-')

    assert 'xxx' in data
    assert 'xxx' in redis.get('cache-b')

    data = cached_body(Document(slug='b', title='B', body='xxx', active=True),
            'cache-')

    assert 'xxx' in data
    assert 'xxx' in redis.get('cache-b')

def test_invalidator(database):
    @invalidator('cache-')
    def fake_endpoint():
        return 'response'

    data = cached_body(Document(slug='c', title='C', body='xxx', active=True),
            'cache-')

    assert 'xxx' in data
    assert 'xxx' in redis.get('cache-c')

    with app.test_request_context('/', method='POST'):
        request.view_args['slug'] = 'c'

        assert 'xxx' in redis.get('cache-c')

        fake_endpoint()

        assert 'xxx' in redis.get('cache-c')

    # with app.test_request_context('/', method='POST'):
    #     request.view_args['slug'] = 'c'

    #     assert 'xxx' in redis.get('cache-c')

    #     fake_endpoint()

    #     assert not redis.get('cache-c')
