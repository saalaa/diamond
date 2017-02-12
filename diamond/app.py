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

from flask import Flask
from diamond.utils import env, secret


app = Flask(__name__)

app.config.update({
    'SQL_DEBUG': env('SQL_DEBUG', False, cast=bool),
    'FLASK_DEBUG': env('FLASK_DEBUG', False, cast=bool),
    'TESTING': env('TESTING', False, cast=bool),
    'BABEL_TRANSLATION_DIRECTORIES': 'i18n',
    'HOST': env('HOST', '0.0.0.0'),
    'PORT': env('PORT', 5000, cast=int),
    'SQLALCHEMY_DATABASE_URI': '',
    'REDIS_URL': env('REDIS_URL', 'redis://mock'),
    'SECRET_KEY': env('SECRET_KEY', secret()),
    'MAIL_SERVER': env('MAIL_SERVER'),
    'MAIL_PORT': env('MAIL_PORT', 587, cast=int),
    'MAIL_USERNAME': env('MAIL_USERNAME'),
    'MAIL_PASSWORD': env('MAIL_PASSWORD'),
    'MAIL_USE_TLS': env('MAIL_USE_TLS', 'yes', cast=bool),
    'MAIL_USE_SSL': env('MAIL_USE_SSL', '', cast=bool),
    'MAIL_DEFAULT_SENDER': env('MAIL_DEFAULT_SENDER',
        'diamond-wiki@example.com')
})

# Fix legacy default
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database heuristics
if env('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = env('DATABASE_URL')

if env('SQLALCHEMY_DATABASE_URI'):
    app.config['SQLALCHEMY_DATABASE_URI'] = env('SQLALCHEMY_DATABASE_URI')

if not app.config['SQLALCHEMY_DATABASE_URI']:
    if app.config['FLASK_DEBUG']:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/diamond.db'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.expanduser('~/diamond.db')

# Merge configuration file
if env('FLASK_CONFIG'):
    app.config.from_envvar('FLASK_CONFIG')

# The modules below expand on the app just created and must be imported for the
# app to do anything at all, hence the imports and NOQA markers.

import diamond.cli      # NOQA
import diamond.filters  # NOQA
import diamond.i18n     # NOQA
import diamond.auth     # NOQA
import diamond.tasks    # NOQA
import diamond.routes   # NOQA
import diamond.admin    # NOQA
import diamond.user     # NOQA
import diamond.errors   # NOQA
