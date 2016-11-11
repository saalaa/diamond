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

from diamond import app
from diamond.utils import env, secret, get_int_arg

def test_env():
    assert env('PATH')
    #assert env('PATH', cast=int) is None

def test_secret():
    assert secret(1, domain='a') == 'a'

def test_get_int_arg():
    with app.test_request_context('/?xxx=42'):
        assert get_int_arg('yyy') == None
        assert get_int_arg('yyy', 100) == 100

        assert get_int_arg('xxx') == 42
        assert get_int_arg('xxx', 100) == 42

        value = get_int_arg('xxx')

        assert type(value) is int
