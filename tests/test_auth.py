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

import re
import pytest
import six

from diamond.app import app
from diamond.cli import init_db, drop_db
from diamond.maths import hash

CSRF_RE = re.compile(r'_csrf_token" value="(.*)">$', re.MULTILINE)


@pytest.fixture
def client():
    drop_db()
    init_db()

    return app.test_client()


def extract_csrf_token(client, url):
    data = client.get(url).data

    # Python 3 compatibility
    if type(data) is not str:
        data = data.decode("utf-8")

    match = CSRF_RE.search(data)

    if not match:
        raise Exception('URL does not contain a CSRF token')

    return match.group(1)


def test_sign_up(client):
    csrf = extract_csrf_token(client, '/auth/sign-up')
    resp = client.post('/auth/sign-up', data={'_csrf_token': csrf, 'name': 'A',
        'password': 'xxx', 'checksum': 'nope', 'answer': 'nope'})

    assert six.b('You failed to answer the simple maths question') in resp.data

    csrf = extract_csrf_token(client, '/auth/sign-up')
    resp = client.post('/auth/sign-up', data={'_csrf_token': csrf, 'name': 'A',
        'password': 'xxx', 'checksum': hash('1'), 'answer': '1'})

    assert resp.status_code == 302

    resp = client.get('/auth/sign-out')

    csrf = extract_csrf_token(client, '/auth/sign-up')
    resp = client.post('/auth/sign-up', data={'_csrf_token': csrf, 'name': 'A',
        'password': 'xxx', 'checksum': hash('1'), 'answer': '1'})

    assert six.b('This user name is unavailable') in resp.data

    csrf = extract_csrf_token(client, '/auth/sign-in')
    resp = client.post('/auth/sign-in', data={'_csrf_token': csrf, 'name': 'A',
        'password': 'yyy'})

    assert six.b('Wrong user name or password') in resp.data

    csrf = extract_csrf_token(client, '/auth/sign-in')
    resp = client.post('/auth/sign-in', data={'_csrf_token': csrf, 'name': 'A',
        'password': 'xxx'})

    assert resp.status_code == 302
