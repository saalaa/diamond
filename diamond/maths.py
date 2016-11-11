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

import hashlib

from random import choice
from operator import add, sub# , mul

OPERATORS = [
    (add, 'plus', '+'),
    (sub, 'minus', '-'),
    # (mul, 'multiplied by', 'by', '*')
]

NUMBERS = [
    (0, 'zero', '0'),
    (1, 'one', '1'),
    (2, 'two', '2'),
    (3, 'three', '3'),
    (4, 'four', '4'),
    (5, 'five', '5'),
    (6, 'six', '6'),
    (7, 'seven', '7'),
    (8, 'eight', '8'),
    (9, 'nine', '9'),
    (10, 'ten', '10')
]

def pick():
    a = choice(NUMBERS)
    op = choice(OPERATORS)
    b = choice(NUMBERS)

    if op[0] is sub:
        b = choice(NUMBERS[:a[0] + 1])

    return a, op, b

def compute(a, op, b):
    return op[0](a[0], b[0])

def speak(a, op, b):
    return '%s %s %s' % (choice(a[1:]), choice(op[1:]), choice(b[1:]))

def hash(result):
    return hashlib.sha256(str(result)).hexdigest()

def generate():
    (a, op, b) = pick()

    return compute(a, op, b), speak(a, op, b)
