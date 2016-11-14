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

from diamond.cli import drop_db, init_db
from diamond.models import Parameter, param

@pytest.fixture
def database():
    drop_db()
    init_db()

def test_all(database):
    Parameter.clear_cache()

    assert Parameter.cache is None
    assert Parameter.timestamp is None

    assert len(Parameter.get_all()) == 0

    assert Parameter.get('xxx') == ''
    assert Parameter.get('xxx', 42) == 42

    assert len(Parameter.get_all()) == 0

    Parameter.set('xxx', 666)

    assert len(Parameter.get_all()) == 1

    assert Parameter.cache is not None
    assert Parameter.timestamp is not None

    assert Parameter.get('xxx') != ''
    assert Parameter.get('xxx', 42) == '666'

    assert Parameter.get('xxx', 42, int) == 666

    assert Parameter.cache is not None
    assert Parameter.timestamp is not None

    Parameter.set('xxx', 42)

    assert len(Parameter.get_all()) == 1

    assert param('xxx', 666, cast=int) == 42
