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

from flask import request
from diamond.redis import redis

def cached(prefix, duration):
    def wrap(f):
        def cached_view(*args, **kwargs):
            slug = request.view_args.get('slug', '')

            cached_value = redis.get(prefix + slug)

            if cached_value:
                return cached_value, 200

            response = f(*args, **kwargs)

            if type(response) is tuple:
                data, status_code = response

                if not status_code == 200:
                    return response

                redis.set(prefix + slug, data, duration)

            return response

        cached_view.__name__ = f.__name__

        return cached_view

    return wrap

def invalidator(prefix):
    def wrap(f):
        def invalidator_view(*args, **kwargs):
            slug = request.view_args.get('slug', '')

            response = f(*args, **kwargs)

            if request.method == 'POST':
                redis.delete(prefix + slug)

            return response

        invalidator_view.__name__ = f.__name__

        return invalidator_view

    return wrap
