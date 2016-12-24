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

import codecs

from os import listdir, getcwd, path
from diamond.app import app
from diamond.db import db
from diamond.redis import redis
from diamond.models import Document, Metadata
from diamond.formatter import parse

FIXTURES_DIR = 'fixtures'


def clear_cache():
    '''Clear all data from Redis.'''
    redis.flushdb()

    print(' * Cache cleared (%s)' % app.config['REDIS_URL'])


def init_db():
    '''Create all database entities.'''
    db.create_all()

    print(' * Database created (%s)' % app.config['SQLALCHEMY_DATABASE_URI'])


def drop_db():
    '''Destroy all database entities (and data).'''
    db.drop_all()

    print(' * Database destroyed (%s)' % app.config['SQLALCHEMY_DATABASE_URI'])


def load_fixtures():
    '''Load fixtures into the database.'''
    cwd = getcwd()
    dir = path.join(cwd, FIXTURES_DIR)

    for filename in listdir(dir):
        file = path.join(dir, filename)

        if path.isfile(file) and file.endswith('.md'):
            print(' * Loading %s' % filename)

            body = codecs.open(file, 'r', 'utf-8') \
                    .read()

            parsed = parse(body)

            slug = filename[:-3]
            title = parsed['title'] or slug

            Metadata.deactivate(slug)
            Document.deactivate(slug)

            for key, values in parsed['meta'].items():
                for value in values:
                    Metadata(slug=slug, key=key, value=value) \
                            .save()

            Document(slug=slug, title=title, body=body) \
                            .save()

            db.session.commit()

    print(' * Fixtures loaded (%s)' % app.config['SQLALCHEMY_DATABASE_URI'])


app.cli.command('clear-cache')(clear_cache)
app.cli.command('init-db')(init_db)
app.cli.command('drop-db')(drop_db)
app.cli.command('load-fixtures')(load_fixtures)
