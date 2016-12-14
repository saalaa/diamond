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

import json
import diamond

from flask import request, render_template, redirect, url_for, flash, g, \
        session
from diamond.app import app
from diamond.formatter import convert, parse
from diamond.auth import current_user
from diamond.diff import unified_diff
from diamond.db import db
from diamond.models import Document, Metadata, Parameter, param
from diamond.utils import secret, get_int_arg
from diamond.caching import cached_body, invalidator


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secret(16)

    return session['_csrf_token']


@app.before_request
def set_globals():
    g.cached_body = cached_body
    g.version = diamond.__version__
    g.param = param
    g.csrf_token = generate_csrf_token


@app.before_request
def csrf_check():
    if request.method == "POST" and not request.path == '/preview':
        token = session.pop('_csrf_token', None)
        if not token == request.form.get('_csrf_token'):
            return render_template('error.j2', error='CSRF error'), 403


@app.route('/robots.txt')
def robots_txt():
    return app.send_static_file('robots.txt')


@app.route('/preview', methods=['POST'])
def preview():
    return convert(request.form['body'] or ''), 200, {
        'Content-Type': 'text/html; charset=utf-8'
    }


@app.route('/')
@app.route('/<slug>')
def read(slug=None):
    version = get_int_arg('version')
    page = Document.get(slug or param('frontpage', 'front-page'),
            version=version)

    if version:
        if not page:
            return render_template('error.j2', error='This version does not '
                    'exist'), 404

        flash('You are viewing version %s of this page' % version)

        return render_template('read.j2', menu=Document.get('main-menu'),
                page=page)

    parsed = parse(page.body)

    if 'page' in parsed['redirect']:
        flash('Redirected from %s' % (page.title or page.slug))

        return redirect(url_for('read', slug=parsed['redirect']['page']))

    return render_template('read.j2', menu=Document.get('main-menu'),
            page=page), 200 if page.id else 404


@app.route('/<slug>.html')
def read_html(slug):
    page = Document.get(slug)

    return convert(page.body), 200 if page.id else 404, {
        'Content-Type': 'text/html; charset=utf-8'
    }


@app.route('/<slug>.md')
def read_md(slug):
    page = Document.get(slug)

    return page.body, 200 if page.id else 404, {
        'Content-Type': 'text/markdown; charset=utf-8'
    }


@app.route('/<slug>.json')
def read_json(slug):
    page = Document.get(slug)

    data = {
        'slug': page.slug,
        'title': page.title,
        'body': page.body,
        'active': page.active,
        'timestamp': page.timestamp.isoformat() if page.timestamp else None
    }

    return json.dumps(data, indent=2), 200 if page.id else 404, {
        'Content-Type': 'application/json; charset=utf-8'
    }


@app.route('/edit/<slug>', methods=['GET', 'POST'])
@invalidator('cache-')
def edit(slug):
    if request.method == 'GET':
        return render_template('edit.j2', menu=Document.get('main-menu'),
                help=Document.get('edit-help'), page=Document.get(slug))

    auth_only = param('auth_only', False)
    if auth_only and not current_user.is_authenticated:
        return render_template('error.j2', error='Edition is limited to '
                'registered users only'), 403

    Metadata.deactivate(slug)
    Document.deactivate(slug)

    parsed = parse(request.form['body'])

    for key, values in parsed['meta'].items():
        for value in values:
            Metadata(slug=slug, key=key, value=value) \
                    .save()

    title = parsed['title'] or slug
    body = request.form['body']
    comment = request.form['comment'] or None

    page = Document(slug=slug, title=title, body=body, comment=comment)

    if current_user.is_authenticated:
        page.author = current_user.slug

    page.save()

    db.session.commit()

    flash('Thank you for your changes. Your attention to detail is '
            'appreciated.')

    return redirect(url_for('read', slug=slug))


@app.route('/search')
@app.route('/search/<path:path>')
def search(path=None):
    query = request.args.get('query', '')

    filters = [item.split('=', 1) for item in path.split('/')] \
            if path else []

    ignores = [item[0] for item in filters]

    hits = Document.search(query, filters)
    facets = Document.facets(hits, ignores=ignores)

    return render_template('search.j2', menu=Document.get('main-menu'),
            help=Document.get('search-help'), query=query, path=path,
            hits=hits, facets=facets, total=Document.count())


@app.route('/title-index')
def title_index():
    return render_template('title-index.j2', menu=Document.get('main-menu'),
            help=Document.get('title-index-help'), titles=Document.titles())


@app.route('/recent-changes')
def recent_changes():
    page_arg = get_int_arg('page', 1)

    changes = Document.changes() \
            .paginate(page_arg, 100)

    return render_template('recent-changes.j2', menu=Document.get('main-menu'),
            help=Document.get('recent-changes-help'), changes=changes)


@app.route('/history/<slug>')
def history(slug):
    page_arg = get_int_arg('page', 1)

    page = Document.get(slug)
    history = page.history() \
            .paginate(page_arg, 100)

    return render_template('history.j2', menu=Document.get('main-menu'),
            help=Document.get('history-help'), page=page, history=history)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if not current_user.admin:
        return render_template('error.j2', error='You are not allowed to '
                'change settings'), 403

    if request.method == 'GET':
        return render_template('settings.j2', menu=Document.get('main-menu'),
                help=Document.get('settings-help'))

    params = request.form.get('params', '')
    for key in params.split():
        if not key:
            pass

        Parameter.set(key, request.form.get(key, ''))

    db.session.commit()

    Parameter.clear_cache()

    flash('Your changes have been saved')

    return redirect(url_for('settings'))


@app.route('/diff/<slug>/<a>/<b>')
def diff(slug, a, b):
    doc_a = Document.get(slug, int(a))
    doc_b = Document.get(slug, int(b))

    body_a = (doc_a.body or '').splitlines()
    body_b = (doc_b.body or '').splitlines()

    name_a = '%s v%s' % (slug, a)
    name_b = '%s v%s' % (slug, b)

    diff = unified_diff(body_a, body_b, name_a, name_b)

    return render_template('diff.j2', menu=Document.get('main-menu'),
            help=Document.get('diff-help'), page=Document.get(slug), diff=diff)


@app.route('/deactivate/<slug>', methods=['GET', 'POST'])
@invalidator('cache-')
def deactivate(slug):
    if request.method == 'GET':
        return render_template('deactivate.j2', menu=Document.get('main-menu'),
                help=Document.get('deactivate-help'))

    if not current_user.admin:
        return render_template('error.j2', error='You are not allowed to '
                'deactivate this page'), 403

    Document.deactivate(slug)
    Metadata.deactivate(slug)

    db.session.commit()

    return redirect(url_for('read', slug=slug))


@app.route('/activate/<slug>', methods=['GET', 'POST'])
@invalidator('cache-')
def activate(slug):
    version = get_int_arg('version')

    if not version:
        return render_template('error.j2', error='Missing version parameter')

    if request.method == 'GET':
        return render_template('activate.j2', menu=Document.get('main-menu'),
                help=Document.get('activate-help'))

    if not current_user.admin:
        return render_template('error.j2', error='You are not allowed to '
                'activate this page'), 403

    page = Document.get(slug, version)

    parsed = parse(page.body)

    for key, values in parsed['meta'].items():
        for value in values:
            Metadata(slug=slug, key=key, value=value) \
                    .save()

    page.save()

    db.session.commit()

    return redirect(url_for('read', slug=slug))


@app.route('/manifest')
def manifest():
    return render_template('manifest.j2', pages=Document.titles())


@app.route('/errors')
def errors():
    raise Exception()
