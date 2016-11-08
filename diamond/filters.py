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

from collections import OrderedDict
from jinja2 import Markup
from slugify import slugify
from diamond.app import app
from diamond.formatter import convert

WORD_PATTERN = r'[A-Z][a-z]+'

@app.template_filter('slug')
def slug(text):
    return slugify(text)

@app.template_filter('format')
def format(text):
    return Markup(convert(text))

@app.template_filter('letters')
def letters(items):
    letters = set()
    for item in items:
        letters.add(item[0].lower())

    return list(letters)

@app.template_filter('words')
def words(items):
    regexp = re.compile(WORD_PATTERN)

    words = {}
    for item in items:
        for word in regexp.findall(item):
            words.setdefault(word, []) \
                    .append(item)

    words = sorted(words.items(), key=lambda t: t[0])

    return OrderedDict(words)

@app.template_filter('title')
def title(title):
    title = re.sub('_', ' ', title)
    title = re.sub('([a-z])([A-Z])', r'\1 \2', title)

    return title

@app.template_filter('pluralize')
def pluralize(number, singular='', plural='s'):
    return (singular if number == 1 else plural) % number
