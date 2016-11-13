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
from diamond.filters import pluralize

def test_pluralize():
    assert pluralize(0, '%d a', '%d b') == '0 a'
    assert pluralize(1, '%d a', '%d b') == '1 a'
    assert pluralize(2, '%d a', '%d b') == '2 b'

    assert pluralize(0.1, '%.2f a', '%.2f b') == '0.10 a'
    assert pluralize(1.0, '%.2f a', '%.2f b') == '1.00 a'
    assert pluralize(2.3, '%.2f a', '%.2f b') == '2.30 b'
