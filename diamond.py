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

__version__ = '0.3'

import re, json, markdown, datetime

from collections import OrderedDict

from jinja2 import Markup
from flask import Flask, request, render_template, redirect, url_for, g

from markdown.extensions.wikilinks import WikiLinkExtension, WikiLinks
from markdown.extensions.codehilite import CodeHiliteExtension

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, String, Text, Integer, Boolean, \
        DateTime, desc, func

WIKILINK_PATTERN = r'\[\[([\w0-9\(\)\'_ -]+)\]\]'
WORD_PATTERN = r'[A-Z][a-z]+'

Base = declarative_base()

Engine = create_engine('sqlite:///diamond.db', convert_unicode=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

db = scoped_session(Session)


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    mtime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    active = Column(Boolean, nullable=False, default=0)

    @property
    def meta(self):
        return Metadata.get(self.name)

    @classmethod
    def count(cls):
        return db.query(Document) \
                .filter(Document.active == True) \
                .count()

    @classmethod
    def get(cls, name):
        document = db.query(Document) \
                .filter(Document.name == name) \
                .filter(Document.active == True) \
                .one_or_none()

        if not document:
            document = Document(name=name, body='Describe [[%s]] here.' %
                    name.replace('_', ' '))

        return document

    @classmethod
    def changes(cls):
        return db.query(Document) \
                .order_by(desc(Document.mtime)) \
                .limit(100)

    @classmethod
    def titles(cls):
        items = db.query(Document) \
                .filter(Document.active == True) \
                .order_by(Document.name)

        return [item.name for item in items]

    @classmethod
    def search(cls, query, fulltext, filters=None):
        names = None
        if filters:
            filters = [Metadata.search(key, value) for key, value in filters]
            names = reduce(lambda acc, x: acc if acc is None else \
                    acc.intersection(x), filters)

        items = db.query(Document.name) \
                .filter(Document.active == True) \
                .order_by(Document.name)

        if names is not None:
            items = items.filter(Document.name.in_(names))

        if query:
            if fulltext:
                items = items.filter(Document.body.like('%' + query + '%'))
            else:
                items = items.filter(Document.name.like('%' + query + '%'))

        return [item[0] for item in items]

    @classmethod
    def facets(cls, names, ignores=None, all=False):
        ignores = ignores or []

        items = db.query(Metadata.key, Metadata.value, func.count()) \
                .filter(Metadata.name.in_(names)) \
                .group_by(Metadata.key, Metadata.value) \
                .order_by(Metadata.key, Metadata.value)

        facets = {}
        for item in items:
            if item[0] in ignores:
                continue

            facets.setdefault(item[0], []) \
                    .append((item[1], item[2]))

        return facets

    @classmethod
    def deactivate(cls, name, commit=True):
        item = Document.get(name)

        item.active = False
        db.add(item)

        if commit:
            db.commit()

    def save(self, commit=True):
        Document.deactivate(self.name, False)
        Metadata.deactivate(self.name, False)

        self.active = True
        db.add(self)

        if commit:
            db.commit()

    def history(self):
        return db.query(Document) \
                .filter(Document.name == self.name) \
                .order_by(desc(Document.mtime)) \
                .limit(100)


class Metadata(Base):
    __tablename__ = 'metadata'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

    @classmethod
    def get(self, name):
        return db.query(Metadata) \
                .filter(Metadata.name == name) \
                .order_by(Metadata.key, Metadata.value)

    @classmethod
    def search(self, key, value):
        items = db.query(Metadata.name) \
                .filter(Metadata.key == key) \
                .filter(Metadata.value == value) \
                .order_by(Metadata.key, Metadata.value)

        return set([item[0] for item in items])

    @classmethod
    def deactivate(cls, name, commit=True):
        for item in Metadata.get(name):
            db.delete(item)

        if commit:
            db.commit()

    def save(self, commit=True):
        db.add(self)

        if commit:
            db.commit()


#Base.metadata.create_all(engine)

class ExtendedWikiLinkExtension(WikiLinkExtension):
    def extendMarkdown(self, md, md_globals):
        self.md = md

        wikilinkPattern = WikiLinks(WIKILINK_PATTERN, self.getConfigs())
        wikilinkPattern.md = md

        md.inlinePatterns.add('wikilink', wikilinkPattern, '<not_strong')

def parse_metadata(text):
    md = markdown.Markdown(extensions=['markdown.extensions.meta'])
    md.convert(text)

    return getattr(md, 'Meta', {})

app = Flask(__name__)

app.config.update({
    'SECRET_KEY': 'si le lilas a sali le lis' # Unimportant in our case
})

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()

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

@app.template_filter('letters')
def letters(items):
    letters = set()
    for item in items:
        letters.add(item[0].lower())

    return list(letters)

@app.template_filter('words')
def words(items):
    regexp = re.compile(WORD_PATTERN)

    words = {}
    for item in items:
        for word in regexp.findall(item):
            words.setdefault(word, []) \
                    .append(item)

    words = sorted(words.items(), key=lambda t: t[0])

    return OrderedDict(words)

@app.template_filter('title')
def title(title):
    title = re.sub('_', ' ', title)
    title = re.sub('([a-z])([A-Z])', r'\1 \2', title)

    return title

@app.template_filter('pluralize')
def pluralize(number, singular='', plural='s'):
    return (singular if number == 1 else plural) % number

@app.route('/preview', methods=['POST'])
def preview():
    return format(request.form['body'] or ''), 200, {
            'Content-Type': 'text/html; charset=utf-8' }

@app.route('/')
@app.route('/<name>')
def read(name='FrontPage'):
    page = Document.get(name)

    return render_template('read.j2', menu=Document.get('MainMenu'),
            page=page, thank=request.args.get('thank', False)), \
            200 if page.id else 404

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
        'body': page.body,
        'active': page.active,
        'mtime': page.mtime.isoformat() if page.mtime else None
    }

    return json.dumps(page, indent=2), 200 if page.id else 404, {
            'Content-Type': 'application/json; charset=utf-8' }

@app.route('/edit/<name>', methods=['GET', 'POST'])
def edit(name):
    if request.method == 'GET':
        return render_template('edit.j2', menu=Document.get('MainMenu'),
                help=Document.get('EditHelp'), page=Document.get(name))

    for key, values in parse_metadata(request.form['body']).items():
        for value in values:
            Metadata(name=name, key=key, value=value) \
                    .save(False)

    Document(name=name, body=request.form['body']) \
            .save()

    return redirect(url_for('read', name=name, thank='yes'))

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

    return render_template('search.j2', menu=Document.get('MainMenu'),
            help=Document.get('SearchHelp'), query=query, fulltext=fulltext,
            path=path, hits=hits, facets=facets, total=Document.count())

@app.route('/titles')
def titles():
    return render_template('titles.j2', menu=Document.get('MainMenu'),
            help=Document.get('TitlesHelp'), titles=Document.titles())

@app.route('/words')
def words():
    return render_template('words.j2', menu=Document.get('MainMenu'),
            help=Document.get('WordsHelp'), titles=Document.titles())

@app.route('/changes')
def changes():
    return render_template('changes.j2', menu=Document.get('MainMenu'),
            help=Document.get('ChangesHelp'), changes=Document.changes())

@app.route('/history/<name>')
def history(name):
    return render_template('history.j2', menu=Document.get('MainMenu'),
            help=Document.get('ChangesHelp'), page=Document.get(name))

if __name__ == '__main__':
    app.run()
