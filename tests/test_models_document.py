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
from diamond.models import Document, Metadata


@pytest.fixture
def database():
    db.drop_all()
    db.create_all()

    Document(slug='a', title='A', body='111').save()

    db.session.commit()

    Document.deactivate('a')

    db.session.commit()

    Document(slug='a', title='A', body='222').save()
    Document(slug='b', title='B', body='111').save()
    Document(slug='c', title='C', body='111').save()

    Metadata(slug='a', key='x', value='1').save()
    Metadata(slug='a', key='y', value='2').save()
    Metadata(slug='b', key='x', value='1').save()
    Metadata(slug='b', key='x', value='2').save()

    db.session.commit()


def test_initial(database):
    assert Document(slug='awerty').initial == 'a'
    assert Document(title='QWERTY').initial == 'q'
    assert Document(slug='awerty', title='QWERTY').initial == 'q'

    assert Document.get('a').initial == 'a'
    assert Document.get('b').initial == 'b'


def test_timestamp(database):
    assert Document().ymd is None
    assert Document().hm is None
    assert Document().ymd_hm is None

    assert Document.get('a').ymd is not None
    assert Document.get('a').hm is not None
    assert Document.get('a').ymd_hm is not None


def test_meta(database):
    assert Document.get('a').meta() != []
    assert Document.get('b').meta() != []
    assert Document.get('c').meta() == []
    assert Document.get('d').meta() == []


def test_count(database):
    assert Document.count() == 3


def test_get(database):
    assert Document.get('a').id is not None
    assert Document.get('b').id is not None
    assert Document.get('c').id is not None
    assert Document.get('d').id is None

    assert '222' in Document.get('a').body
    assert '111' in Document.get('b').body
    assert '111' in Document.get('c').body
    assert 'Describe' in Document.get('d').body

    doc = Document.get('a', '1')

    assert '111' in doc.body
    assert not doc.active


def test_titles(database):
    titles = Document.titles().all()

    assert len(titles) == 3


def test_changes(database):
    changes = Document.changes().all()

    assert len(changes) == 4


def test_history(database):
    history = Document.get('a') \
            .history() \
            .all()

    assert len(history) == 2

    history = Document.get('b') \
            .history() \
            .all()

    assert len(history) == 1

    history = Document.get('c') \
            .history() \
            .all()

    assert len(history) == 1


def test_search(database):
    docs = Document.search('')

    assert len(docs) == 3

    docs = Document.search('111')

    assert len(docs) == 2

    docs = Document.search('222')

    assert len(docs) == 1

    docs = Document.search('333')

    assert len(docs) == 0

    docs = Document.search('', filters=[('x', '1')])

    assert len(docs) == 2

    docs = Document.search('', filters=[('x', '1'), ('x', '2')])

    assert len(docs) == 1

    docs = Document.search('', filters=[('x', '1'), ('y', '2')])

    assert len(docs) == 1

    docs = Document.search('111', filters=[('x', '1')])

    assert len(docs) == 1


def test_facets(database):
    docs = Document.search('')
    facets = Document.facets(docs)

    assert 'x' in facets
    assert 'y' in facets

    docs = Document.search('', filters=[('x', '3')])
    facets = Document.facets(docs, ignores=['x'])

    assert not facets

    docs = Document.search('', filters=[('x', '1')])
    facets = Document.facets(docs, ignores=['x'])

    assert 'y' in facets
