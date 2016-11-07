import json

from flask import request, render_template, redirect, url_for, flash, g

from app import app
from md import convert, parse
from auth import current_user
from diff import unified_diff
from db import db
from model_document import Document
from model_metadata import Metadata
from model_parameter import Parameter, param

@app.before_first_request
def auto_init():
    db.create_all()

@app.before_request
def set_globals():
    g.param = param

@app.route('/robots.txt')
def robots_txt():
    return app.send_static_file('robots.txt')

@app.route('/preview', methods=['POST'])
def preview():
    return convert(request.form['body'] or ''), 200, {
            'Content-Type': 'text/html; charset=utf-8' }

@app.route('/')
@app.route('/<name>')
def read(name=None):
    version = request.args.get('version', None)
    page = Document.get(name or param('frontpage', 'front-page'),
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
        flash('Redirected from %s' % (page.title or page.name))

        return redirect(url_for('read', name=parsed['redirect']['page']))

    return render_template('read.j2', menu=Document.get('main-menu'),
            page=page), 200 if page.id else 404

@app.route('/<name>.html')
def read_html(name):
    page = Document.get(name)

    return format(page.body), 200 if page.id else 404, {
            'Content-Type': 'text/html; charset=utf-8' }

@app.route('/<name>.md')
def read_md(name):
    page = Document.get(name)

    return page.body, 200 if page.id else 404, {
            'Content-Type': 'text/markdown; charset=utf-8' }

@app.route('/<name>.json')
def read_json(name):
    page = Document.get(name)

    page = {
        'name': page.name,
        'title': page.title,
        'body': page.body,
        'active': page.active,
        'mtime': page.mtime.isoformat() if page.mtime else None
    }

    return json.dumps(page, indent=2), 200 if page.id else 404, {
            'Content-Type': 'application/json; charset=utf-8' }

@app.route('/edit/<name>', methods=['GET', 'POST'])
def edit(name):
    if request.method == 'GET':
        return render_template('edit.j2', menu=Document.get('main-menu'),
                help=Document.get('edit-help'), page=Document.get(name))

    auth_only = param('auth_only', False)
    if auth_only and not current_user.is_authenticated:
        return render_template('error.j2', error='Edition is limited to '
                'registered users only'), 403

    parsed = parse(request.form['body'])

    for key, values in parsed['meta'].items():
        for value in values:
            Metadata(name=name, key=key, value=value) \
                    .save()

    title = parsed['title'] or name
    body = request.form['body']
    comment = request.form['comment'] or None

    document = Document(name=name, title=title, body=body, comment=comment)

    if current_user.is_authenticated:
        document.user_slug = current_user.slug

    document.save()

    db.session.commit()

    flash('Thank you for your changes. Your attention to detail is '
            'appreciated.')

    return redirect(url_for('read', name=name))

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
    return render_template('titles.j2', menu=Document.get('main-menu'),
            help=Document.get('title-index-help'), titles=Document.titles())

@app.route('/recent-changes')
def recent_changes():
    return render_template('changes.j2', menu=Document.get('main-menu'),
            help=Document.get('recent-changes-help'),
            changes=Document.changes())

@app.route('/history/<name>')
def history(name):
    return render_template('history.j2', menu=Document.get('main-menu'),
            help=Document.get('history-help'), page=Document.get(name))

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

@app.route('/diff/<name>/<a>/<b>')
def diff(name, a, b):
    doc_a = Document.get(name, int(a))
    doc_b = Document.get(name, int(b))

    body_a = (doc_a.body or '').splitlines()
    body_b = (doc_b.body or '').splitlines()

    name_a = '%s v%s' % (name, a)
    name_b = '%s v%s' % (name, b)

    diff = unified_diff(body_a, body_b, name_a, name_b)

    return render_template('diff.j2', menu=Document.get('main-menu'),
            help=Document.get('diff-help'), page=Document.get(name), diff=diff)

@app.route('/deactivate/<name>', methods=['GET', 'POST'])
def deactivate(name):
    if request.method == 'GET':
        return render_template('deactivate.j2', menu=Document.get('main-menu'),
                help=Document.get('deactivate-help'))

    if not current_user.admin:
        return render_template('error.j2', error='You are not allowed to '
                'deactivate this page'), 403

    Document.deactivate(name)
    Metadata.deactivate(name)

    db.session.commit()

    return redirect(url_for('read'))
