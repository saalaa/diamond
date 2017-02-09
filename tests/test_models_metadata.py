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
from diamond.models import Metadata


@pytest.fixture
def database():
    db.drop_all()
    db.create_all()


def test_all(database):
    Metadata(slug='AAA', key='a', value='1').save()
    Metadata(slug='AAA', key='b', value='2').save()
    Metadata(slug='BBB', key='a', value='1').save()

    db.session.commit()

    assert len(Metadata.get('AAA')) == 2
    assert len(Metadata.get('BBB')) == 1

    results = Metadata.search('a', '1')

    assert 'AAA' in results
    assert 'BBB' in results

    assert len(results) == 2

    results = Metadata.search('b', '2')

    assert 'AAA' in results
    assert 'BBB' not in results

    assert len(results) == 1

    Metadata.deactivate('AAA')

    db.session.commit()

    assert 'AAA' not in Metadata.search('a', '1')
    assert 'AAA' not in Metadata.search('b', '2')

    assert len(Metadata.get('AAA')) == 0
