import json

from flask import request, render_template, redirect, url_for, flash

from .app import app
from .md import convert, parse
from .models import Document, Metadata
from .auth import current_user

@app.route('/robots.txt')
def robots_txt():
    return app.send_static_file('robots.txt')

@app.route('/preview', methods=['POST'])
def preview():
    return format(request.form['body'] or ''), 200, {
            'Content-Type': 'text/html; charset=utf-8' }

@app.route('/')
@app.route('/<name>')
def read(name=None):
    page = Document.get(name or app.config['FRONTPAGE'])

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

    parsed = parse(request.form['body'])

    for key, values in parsed['meta'].items():
        for value in values:
            Metadata(name=name, key=key, value=value) \
                    .save(False)

    title = parsed['title'] or name
    body = request.form['body']
    comment = request.form['comment'] or None

    document = Document(name=name, title=title, body=body, comment=comment)

    if current_user.is_authenticated:
        document.user_slug = current_user.slug

    document.save()

    flash('Thank you for your changes. Your attention to detail is '
            'appreciated.')

    return redirect(url_for('read', name=name))

@app.route('/search')
@app.route('/search/<path:path>')
def search(path=None):
    query = request.args.get('query', '')
    fulltext = request.args.get('fulltext', '')

    filters = [item.split('=', 1) for item in path.split('/')] \
            if path else []

    ignores = [item[0] for item in filters]

    hits = Document.search(query, fulltext, filters)
    facets = Document.facets(hits, ignores=ignores)

    return render_template('search.j2', menu=Document.get('main-menu'),
            help=Document.get('search-help'), query=query, fulltext=fulltext,
            path=path, hits=hits, facets=facets, total=Document.count())

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
