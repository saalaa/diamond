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

import difflib

from markupsafe import Markup, escape

def markup_new(text):
    return Markup('<span class="line-new">') + escape(text) + Markup('</span>')

def markup_old(text):
    return Markup('<span class="line-old">') + escape(text) + Markup('</span>')

def markup_common(text):
    return escape(text)

def markup_inline(text, markup):
    return markup(text) \
            .replace('\x00+', Markup('<span class="chunk-added">')) \
            .replace('\x00-', Markup('<span class="chunk-deleted">')) \
            .replace('\x00^', Markup('<span class="chunk-changed">')) \
            .replace('\x01', Markup('</span>'))

def unified_diff(a, b, name_a=None, name_b=None):
    if name_a and name_b:
        yield markup_old(name_a)
        yield markup_new(name_b)

        yield ''

    for old, new, changed in difflib._mdiff(a, b):
        if changed:
            if not old[0]:
                yield markup_new(new[1][2:])
            elif not new[0]:
                yield markup_old(old[1][2:])
            else:
                yield markup_inline(old[1], markup_old)
                yield markup_inline(new[1], markup_new)
        else:
            yield markup_common(old[1])
