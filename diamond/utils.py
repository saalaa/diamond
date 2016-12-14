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

import os
import random
import string
import functools

from flask import request

# The import statement below allows exporting symbols, hence the NOQA marker.

from werkzeug.utils import cached_property # NOQA

DEFAULT_DOMAIN = string.digits + string.ascii_uppercase + \
        string.ascii_lowercase


def memoized(obj):
    obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)

        if key not in obj.cache:
            obj.cache[key] = obj(*args, **kwargs)

        return obj.cache[key]

    return memoizer


def env(variable, default=None, cast=None):
    value = os.environ.get(variable, default)

    if cast:
        value = cast(value)

    return value


def secret(size=42, domain=DEFAULT_DOMAIN):
    return ''.join(random.sample(domain, size))


def get_int_arg(name, default=None):
    value = request.args.get(name)

    if value:
        try:
            value = int(value)
        except:
            value = default

    return value or default
