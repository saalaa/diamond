#!/usr/bin/env python

# Copyright (C) 1999, 2000 Martin Pool <mbp@humbug.org.au>
# Copyright (C) 2003 Kimberley Burchett http://www.kimbly.com/
# Copyright (C) 2016 Benoit Myard <myardbenoit@gmail.com>

# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA

__version__ = '0.3';

import os, re, json, sqlite3, markdown

from time import localtime, strftime, time

from jinja2 import Markup
from flask import Flask, request, render_template, redirect, url_for, g, \
    sessions, flash

from markdown.extensions.wikilinks import WikiLinkExtension, WikiLinks
from markdown.extensions.codehilite import CodeHiliteExtension

WIKILINK_PATTERN = r'\[\[([\w0-9\(\)\'_ -]+)\]\]'

class ExtendedWikiLinkExtension(WikiLinkExtension):
    def extendMarkdown(self, md, md_globals):
        self.md = md

        wikilinkPattern = WikiLinks(WIKILINK_PATTERN, self.getConfigs())
        wikilinkPattern.md = md

        md.inlinePatterns.add('wikilink', wikilinkPattern, "<not_strong")

def get_db():
    if not hasattr(g, 'db'):
        g.db = sqlite3.connect('diamond.db')
        g.db.row_factory = sqlite3.Row

    return g.db

def parse_metadata(text):
    md = markdown.Markdown(extensions=['markdown.extensions.meta'])
    md.convert(text)

    return getattr(md, 'Meta', {})

class Document:
    def __init__(self, name=None, body=None, mtime=None, meta=None,
            id=None, exists=False):
        self.id = id
        self.name = name
        self.body = body or ''
        self.mtime = mtime
        self.meta = meta or {}

        self.exists = exists

    @classmethod
    def get(cls, name):
        db = get_db()

        cr = db.execute('''
            SELECT name, body, mtime
              FROM documents
             WHERE name = ?
               AND active = 1
             LIMIT 1
            ''', [name])

        row = cr.fetchone()

        if not row:
            return cls(name, 'Describe [[%s]] here.' % name.replace('_', ' '))

        document = cls(row['name'], row['body'], row['mtime'],
                meta=cls.metadata(name), exists=True)

        return document

    @classmethod
    def metadata(cls, name):
        db = get_db()

        cr = db.execute('''
            SELECT key, value
              FROM metadata
             WHERE document_name = ?
             ORDER BY key, value
            ''', [name])

        metadata = {}
        for row in cr.fetchall():
            metadata.setdefault(row['key'], []) \
                .append(row['value'])

        return metadata

    @classmethod
    def titles(cls):
        db = get_db()

        cr = db.execute('''
            SELECT name
              FROM documents
             WHERE active = 1
             ORDER BY name ASC
            ''')

        titles = []
        for row in cr.fetchall():
            titles.append(row['name'])

        return titles

    @classmethod
    def changes(cls):
        db = get_db()

        cr = db.execute('''
            SELECT name, mtime
              FROM documents
             ORDER BY mtime DESC
             LIMIT 100
            ''')

        titles = []
        for row in cr.fetchall():
            titles.append((row['name'], row['mtime']))

        return titles

    def history(self):
        db = get_db()

        cr = db.execute('''
            SELECT name, mtime
              FROM documents
             WHERE name = ?
             ORDER BY mtime DESC
             LIMIT 100
            ''', [self.name])

        titles = []
        for row in cr.fetchall():
            titles.append((row['name'], row['mtime']))

        return titles

    @classmethod
    def search(cls, query, fulltext, filters=None):
        db = get_db()

        def filter(key, value):
            cr = db.execute('''
                SELECT document_name
                  FROM metadata
                 WHERE key = ?
                   AND value = ?
                ''', [key, value])

            names = set()
            for row in cr.fetchall():
                names.add(row['document_name'])

            return names

        field = 'body' if fulltext else 'name'

        if filters:
            names = None
            for key, value in filters.items():
                result = filter(key, value)

                if not names:
                    names = result
                else:
                    names = names.intersection(result)

            if not names:
                return []

            if query:
                names = ', '.join(['"' + name + '"' for name in names])

                cr = db.execute('''
                    SELECT name
                      FROM documents
                     WHERE active = 1
                       AND name IN (%s)
                       AND %s LIKE ?
                     ORDER BY name ASC
                    ''' % (names, field), [query])
            else:
                names = list(names)
                names.sort()

                return names
        else:
            if query:
                query = '%' + query + '%'

                cr = db.execute('''
                    SELECT name
                      FROM documents
                     WHERE active = 1
                       AND %s LIKE ?
                     ORDER BY name ASC
                    ''' % field, [query])
            else:
                cr = db.execute('''
                    SELECT name
                      FROM documents
                     WHERE active = 1
                     ORDER BY name ASC
                    ''')

        titles = []
        for row in cr.fetchall():
            titles.append(row['name'])

        return titles

    @classmethod
    def facets(cls, names, ignore=None, all=False):
        db = get_db()

        ignore = ignore if ignore is not None else []

        names = ', '.join(['"' + name + '"' for name in names])

        cr = db.execute('''
            SELECT key, value, COUNT(*) AS count
              FROM metadata
             WHERE document_name IN (%s)
             GROUP BY key, value
             ORDER BY key, value ASC
            ''' % names)

        facets = {}
        for row in cr.fetchall():
            if row['key'] in ignore:
                continue

            facets.setdefault(row['key'], []) \
                .append((row['value'], row['count']))

        return facets

    @classmethod
    def count(cls):
        db = get_db()

        cr = db.execute('''
            SELECT COUNT(*) AS count
              FROM documents
             WHERE active = 1
            ''')

        return cr.fetchone()['count']

    def deactivate(self, commit=True):
        db = get_db()

        cr = db.execute('''
            UPDATE documents
               SET active = 0
             WHERE name = ?
            ''', [self.name])

        cr = db.execute('''
            DELETE FROM metadata
             WHERE document_name = ?
            ''', [self.name])

    def save(self):
        db = get_db()

        if self.exists:
            self.deactivate(False)

        cr = db.execute('''
            INSERT INTO documents (name, body, active, mtime)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ''', [self.name, self.body])

        for key, values in self.meta.items():
            for value in values:
                cr = db.execute('''
                    INSERT INTO metadata (document_name, key, value)
                    VALUES (?, ?, ?)
                    ''', [self.name, key, value])

        db.commit()

        self.exists = True

        return True

class Search:
    def __init__(self, query, fulltext, filters):
        self.query = query
        self.fulltext = fulltext
        self.filters = filters or ''

        self.facets = {}
        self.results = []
        self.hits = 0
        self.total = 0

        self.path = '' if not self.filters else '/' + self.filters
        self.query_string = 'query=%s&fulltext=%s' % (self.query,
                self.fulltext)

    def build_filters(self):
        if not self.filters:
            return {}

        filters = {}
        for filter in self.filters.split('/'):
            key, value = filter.split('=', 1)

            filters[key] = value

        return filters

    def execute(self):
        all = not self.query \
                and not self.fulltext \
                and not self.filters

        filters = self.build_filters()
        ignore = filters.keys()

        results = Document.search(self.query, self.fulltext, filters)
        facets = Document.facets(results, ignore=ignore, all=all)
        total = Document.count()

        self.facets = facets
        self.results = results
        self.hits = len(results)
        self.total = total

        return self

class TitleIndex:
    def execute(self):
        titles = Document.titles()
        letters = [title[0] for title in titles]

        letters = set(letters)
        letters = list(letters)

        letters.sort()

        self.results = titles
        self.letters = letters

        return self

class WordIndex:
    def execute(self):
        titles = Document.titles()

        word_re = re.compile('[A-Z][a-z]+')

        mapping = {}
        for name in titles:
            for word in word_re.findall(name):
                mapping.setdefault(word, []) \
                    .append(name)

        words = mapping.keys()
        words.sort()

        letters = [word[0] for word in words]

        letters = set(letters)
        letters = list(letters)

        letters.sort()

        self.results = mapping
        self.letters = letters

        return self

class Changes:
    def execute(self):
        changes = Document.changes()

        self.results = changes

        return self

class History:
    def __init__(self, page):
        self.page = page

    def execute(self):
        history = self.page.history()

        self.results = history

        return self


app = Flask(__name__)

app.config.update({
    'SECRET_KEY': 'si le lilas a sali le lis' # Unimportant in our case
})

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

@app.template_filter('format')
def format(text):
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.meta',
        'markdown.extensions.toc',
        CodeHiliteExtension(guess_lang=False),
        ExtendedWikiLinkExtension(end_url='')
    ])

    html = md.convert(text)

    return Markup(html)

@app.template_filter('title')
def title(title):
    title = re.sub('_', ' ', title)
    title = re.sub('([a-z])([A-Z])', r'\1 \2', title)

    return title

@app.template_filter('pluralize')
def pluralize(number, singular='', plural='s'):
    return (singular if number == 1 else plural) % number

@app.route('/')
@app.route('/<name>')
def read(name=None):
    page = Document.get(name or 'FrontPage')

    if not page.exists:
        return render_template('read.j2', menu=Document.get('MainMenu'),
                page=page), 404

    return render_template('read.j2', menu=Document.get('MainMenu'),
            page=page)

@app.route('/preview/<name>')
def preview(name=None):
    return render_template('preview.j2', page=Document.get(name))

@app.route('/<name>/edit', methods=['GET', 'POST'])
def edit(name):
    page = Document.get(name)

    if request.method == 'POST':
        page.body = request.form['body']
        page.meta = parse_metadata(request.form['body'])

        page.save()

        flash('Thank you for your changes. Your attention to detail is ' \
                'appreciated.')

        return redirect(url_for('read', name=name))

    return render_template('edit.j2', menu=Document.get('MainMenu'),
            help=Document.get('EditHelp'), page=page)

@app.route('/search')
@app.route('/search/<path:facets>')
def search(facets=None):
    query = request.args.get('query', '')
    fulltext = request.args.get('fulltext', '')

    search = Search(query, fulltext, facets) \
        .execute()

    return render_template('search.j2', menu=Document.get('MainMenu'),
            help=Document.get('SearchHelp'), search=search)

@app.route('/titles')
def titles():
    index = TitleIndex() \
        .execute()

    return render_template('titles.j2', menu=Document.get('MainMenu'),
            help=Document.get('TitlesHelp'), index=index)

@app.route('/words')
def words():
    index = WordIndex() \
        .execute()

    return render_template('words.j2', menu=Document.get('MainMenu'),
            help=Document.get('WordsHelp'), index=index)

@app.route('/changes')
def changes():
    changes = Changes() \
        .execute()

    return render_template('changes.j2', menu=Document.get('MainMenu'),
            help=Document.get('ChangesHelp'), changes=changes)

@app.route('/<name>/history')
def history(name):
    page = Document.get(name)

    history = History(page) \
        .execute()

    return render_template('history.j2', menu=Document.get('MainMenu'),
            help=Document.get('ChangesHelp'), history=history, page=page)

if __name__ == '__main__':
    app.run()
