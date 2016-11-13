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

from diamond import app
from diamond.maths import pick, sub, hash, generate

def test_pick():
    op = (None, )
    while op[0] is not sub:
        a, op, b = pick()

    assert b <= a

def test_hash():
    assert hash(42) == '73475cb40a568e8da8a045ced110137e159f890ac4da883b6b17' \
            'dc651b3a8049'

def test_generate():
    result, question = generate()

    assert type(result) is int

    assert 'by' not in question and '*' not in question
    assert 'plus' in question or '+' in question \
            or 'minus' in question or '-' in question
