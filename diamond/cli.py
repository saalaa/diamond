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

import sys
import click
import json
import codecs
import datetime

from flask import render_template
from gunicorn.app import wsgiapp as gunicorn
from os import listdir, getcwd, path
from diamond.app import app
from diamond.db import db
from diamond.models import Document, Metadata
from diamond.formatter import parse
from diamond.tasks import celery, with_celery

FIXTURES_DIR = 'fixtures'


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.timedelta):
            return str(obj)

        return super(JSONEncoder, self).default(obj)


def serialize(key):
    value = app.config[key]

    if value is None:
        return None
    elif type(value) is int:
        return value
    elif type(value) is str:
        return "'%s'" % value
    elif type(value) is bool:
        return 'True' if value else 'False'


def load_fixtures():
    '''Load fixtures into the database.'''
    cwd = getcwd()
    dir = path.join(cwd, FIXTURES_DIR)

    for filename in listdir(dir):
        file = path.join(dir, filename)

        if not path.isfile(file) or not file.endswith('.md'):
            continue

        print(' * Loading %s' % filename)

        slug = filename[:-3]

        page = Document.get(slug=slug)

        if page.id:
            print(' * Document exists, skipping')
            continue

        body = codecs.open(file, 'r', 'utf-8') \
                .read()

        parsed = parse(body)

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


@click.option('-b', '--bind', help='The socket to bind.')
@click.option('-w', '--workers', help='The number of worker processes for '
        'handling requests.')
@click.option('-D', '--daemon', is_flag=True, help='Daemonize the Gunicorn '
        'process.')
@click.option('-u', '--user', help='Switch worker processes to run as this '
        'user.')
@click.option('-g', '--group', help='Switch worker process to run as this '
        'group.')
@click.option('-m', '--umask', help='A bit mask for the file mode on files '
        'written by Gunicorn.')
def web(bind, workers, daemon, user, group, umask):
    '''Runs a production web server (Gunicorn).

    All command line options are passed to Gunicorn as is. See Gunicorn
    documentation for additional information on command line options.
    '''
    print(' * Starting a task worker (Gunicorn)')

    sys.argv.pop(0)
    sys.argv.append('diamond:app')

    gunicorn.run()


@click.option('-D', '--detach', is_flag=True, help='Start worker as a '
        'background process.')
def worker(detach):
    '''Runs a task worker (Celery).

    All command line options are passed to Celery as is. See Celery
    documentation for additional information on command line options.
    '''
    print(' * Starting a task worker (Celery)')

    if not with_celery():
        print(' * Broker not configured, aborting')
        sys.exit(1)

    celery.start()


@click.option('-r', '--raw', is_flag=True, help='Raw output for debugging')
def config(raw):
    '''Dump configuration.

    By default, this command dumps the configuration in a format meant to be
    stored and reloaded as-is.
    '''
    if raw:
        output = JSONEncoder(indent=2) \
                .encode(app.config)
    else:
        output = render_template('config.j2', serialize=serialize)

    print(output)


app.cli.command('load-fixtures')(load_fixtures)
app.cli.command('web')(web)
app.cli.command('worker')(worker)
app.cli.command('config')(config)
