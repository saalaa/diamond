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

import os, re, errno, urllib

from jinja2 import Markup
from flask import Flask, request, render_template, redirect, url_for, flash, \
    sessions

from markdown import markdown
from markdown.extensions.wikilinks import WikiLinkExtension
from markdown.extensions.codehilite import CodeHiliteExtension

from time import localtime, strftime, time

WIKILINK_RE = re.compile(r'^([\w0-9_ -]+)$') # Markdown compatibility

DATA_DIR = 'data/'
CHANGE_LOG = 'data/changes.log'

DATETIME_FMT = '%a %d %b %Y %I:%M %p'

class KeyVal:
    """A key-value pair.  This class is used to represent the metadata
    for individual pages, as well as refinements when browsing."""

    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.count = 0

    def __cmp__(self, other):
        key_lower = self.key.lower()
        other_key_lower = other.key.lower()

        if key_lower < other_key_lower: return -1
        if key_lower > other_key_lower: return 1

        if self.count and other.count:
            if self.count < other.count: return 1
            if self.count > other.count: return -1

        val_lower = self.val.lower()
        other_val_lower = other.val.lower()

        if val_lower < other_val_lower: return -1
        if val_lower > other_val_lower: return 1

        return 0

    def build_url(self):
        return "/%s=%s" % (urllib.quote(self.key), urllib.quote(self.val))

    def build_title(self):
        return self.val or 'No %s' % self.key

class View:
    """A view is the subset of pages that match particular metadata
    key-value pairs.  In fact, it's just the key/value pairs, and the
    pages are handled separately"""

    def __init__(self, pairs=None):
        self.keyvals = pairs or []

    def copy(self, other_view):
        self.keyvals = [keyval for keyval in other_view.keyvals]
        return self

    # narrow the view to only pages that have the given key/value pair.
    def narrow(self, keyval):
        self.keyvals.append(keyval)
        return self

    def contains(self, keyval):
        return keyval in self.keyvals

    def pages(self):
        all_pages = [Page(page_name) for page_name in page_list()]
        return [p for p in all_pages if self.includes(p.metadata())]

    def includes(self, other_view):
        for kv in self.keyvals:
            if kv.val == "":
                # if we have no value, then make sure the other view has no
                # value for this key
                if len([okv for okv in other_view.keyvals if okv.key==kv.key]):
                    return False
            else:
                # if we do have a value, then make sure it's the same as the
                # other view's value for this key
                if kv not in other_view.keyvals:
                    return False
        return True

    def is_empty(self):
        return len(self.keyvals) == 0

    # returns [(String group, String val)]
    def refinements(self, pages):
        potential_refinements = []
        for page in pages:
            for kv in page.metadata().keyvals:
                # ignore refinements that are already contained by this view
                if not self.contains(kv):
                    already_seen = False
                    for ref in potential_refinements:
                        if ref == kv:
                            already_seen = True
                            ref.count = ref.count + 1
                    if not already_seen:
                        kv.count = 1
                        potential_refinements.append(kv)

        # Only include refinements that aren't shared by all pages in the view.
        # Otherwise we sometimes get boring, redundant refinements that "don't
        # add any information"
        result = []
        for refinement in potential_refinements:
            restricts_view = False
            for page in pages:
                if not page.metadata().contains(refinement):
                    restricts_view = True
            if restricts_view:
                result.append(refinement)

        return result

    def build_url(self):
        return ''.join([kv.build_url() for kv in self.keyvals])

    def build_title(self):
        return ', '.join([kv.build_title() for kv in self.keyvals])

# TODO page_name should be name
# TODO Get rid of weird private members
# TODO Simplify save methods
# TODO Work on log handling
class Page:
    def __init__(self, page_name):
        self.page_name = page_name

    def _body_filename(self):
        return os.path.join(DATA_DIR, self.page_name)

    def _metadata_filename(self):
        return os.path.join(DATA_DIR, self.page_name + ".meta")

    def _tmp_filename(self):
        return os.path.join(DATA_DIR, ('#' + self.page_name + '.' + `os.getpid()` + '#'))

    def exists(self):
        try:
            os.stat(self._body_filename())
            return True
        except OSError, er:
            if er.errno == errno.ENOENT:
                return False
            else:
                raise er

    def raw_metadata(self):
        try:
            return open(self._metadata_filename(), 'rt').read()
        except IOError, er:
            if er.errno == errno.ENOENT:
                # just doesn't exist, use default
                return ''
            else:
                raise er

    def metadata(self):
        metatext = self.raw_metadata()
        metatext = metatext.replace("\r\n", "\n")

        view = View()
        for line in metatext.splitlines():
            try:
                (key, val) = str_to_pair(line, ":")
                view.narrow(KeyVal(key.strip(), val.strip()))
            except ValueError, er:
                # ignore invalid metatext lines
                pass
        # add automatic metadata
        return view

    def get_body(self):
        try:
            return open(self._body_filename(), 'rt').read()
        except IOError, er:
            if er.errno == errno.ENOENT:
                # just doesn't exist, use default
                return 'Describe [[%s]] here.' % self.page_name
            else:
                raise er

    def _last_modified(self):
        if not self.exists():
            return None

        ctime = localtime(os.stat(self._body_filename()).st_ctime)

        return strftime(DATETIME_FMT, ctime)

    def _write_file(self, text, filename):
        tmp_filename = self._tmp_filename()
        open(tmp_filename, 'wt').write(text)
        if os.name == 'nt':
            # Bad Bill!  POSIX rename ought to replace. :-(
            try:
                os.remove(filename)
            except OSError, er:
                if er.errno != errno.ENOENT: raise er
        os.rename(tmp_filename, filename)

    def save_body(self, data):
        return self.save_text(data)

    def save_meta(self, data):
        return self.save_metadata(data)

    def save_text(self, newtext):
        self._write_file(newtext, self._body_filename())

        remote = request.remote_addr
        editlog_add(self.page_name, remote)

    def save_metadata(self, newmetatext):
        self._write_file(newmetatext, self._metadata_filename())

        remote = request.remote_addr
        editlog_add(self.page_name, remote)

class Search:
    def __init__(self, query, fulltext=False):
        self.query = query
        self.fulltext = fulltext

        self.results = []
        self.hits = 0
        self.total = 0

        self.executed = False

    def execute(self):
        if (self.fulltext):
            self.fulltext_search()
        else:
            self.title_search()

    def fulltext_search(self):
        regexp = re.compile(self.query, re.IGNORECASE)

        hits = []
        pages = page_list()

        for name in pages:
            body = Page(name).get_body()

            matches = len(regexp.findall(body))

            if matches:
                hits.append((matches, name))

        hits.sort()
        hits.reverse()

        self.results = hits
        self.hits = len(hits)
        self.total = len(pages)

        self.executed = True

    def title_search(self):
        regexp = re.compile(self.query, re.IGNORECASE)

        hits = []
        pages = page_list()

        for name in pages:
            matches = len(regexp.findall(name))

            if matches:
                hits.append((matches, name))

        hits.sort()
        hits.reverse()

        self.results = hits
        self.hits = len(hits)
        self.total = len(pages)

        self.executed = True

class FacetsBrowser:
    def __init__(self, query):
        self.query = []

        self.results = []
        self.hits = 0
        self.total = 0

        self.executed = False

        if query:
            for chunk in query.split('/'):
                if not chunk:
                    continue

                bits = chunk.split('=', 1)

                key = bits[0]
                value = bits[1] if len(bits) == 2 else ''

                self.query.append(KeyVal(key, value))

    def execute(self):
        view = View(self.query)

        pages = page_list()
        hits = view.pages()

        refinements = view.refinements(hits)
        filters = group_refinements(refinements)

        self.hits = len(hits)
        self.total = len(pages)

        self.filters = filters
        self.results = hits

        self.url = view.build_url();
        self.title = view.build_title();

        self.executed = True

class TitleIndex:
    def __init__(self):
        pass

    def execute(self):
        pages = list(page_list())
        pages.sort()

        self.results = pages
        self.letters = [title[0] for title in pages]

class WordIndex:
    def __init__(self):
        pass

    def execute(self):
        pages = list(page_list())

        mapping = {}

        word_re = re.compile('[A-Z][a-z]+')

        for name in pages:
            for word in word_re.findall(name):
                try:
                    mapping[word].append(name)
                except KeyError:
                    mapping[word] = [name]

        words = mapping.keys()
        words.sort()

        self.results = mapping
        self.letters = [title[0] for title in words]

class Changes:
    def execute(self):
        def format(t):
            t = float(t)
            t = localtime(t)
            return strftime(DATETIME_FMT, t)

        lines = editlog_raw_lines()
        lines.reverse()

        lines = [line.split('\t') for line in lines]
        lines = [(title, address, format(t)) for title, address, t in lines]

        self.results = lines


app = Flask(__name__)

app.config.update({
    'SECRET_KEY': 'si le lilas a sali le lis' # Unimportant in our case
})

@app.template_filter('format')
def format(text):
    html = markdown(text, extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.toc',
        CodeHiliteExtension(guess_lang=False),
        WikiLinkExtension(end_url='')
    ])

    return Markup(html)

@app.template_filter('title')
def title(title):
    return re.sub('([a-z])([A-Z])', r'\1 \2', title)

@app.template_filter('pluralize')
def pluralize(number, singular='', plural='s'):
    return (singular if number == 1 else plural) % number

@app.route('/')
@app.route('/<name>')
def show(name=None):
    menu = Page('MainMenu')
    page = Page(name or 'FrontPage')

    return render_template('show.j2', menu=menu, page=page)

@app.route('/<name>/edit', methods=['GET', 'POST'])
def edit(name):
    menu = Page('MainMenu')
    help = Page('EditHelp')

    page = Page(name)

    if request.method == 'POST':
        page.save_body(request.form['body'])
        page.save_meta(request.form['meta'])

        flash('Thank you for your changes. Your attention to detail is appreciated.')

        return redirect(url_for('show', name=name))

    return render_template('edit.j2', menu=menu, help=help, page=page)

@app.route('/titles')
def titles():
    menu = Page('MainMenu')
    help = Page('TitlesHelp')

    index = TitleIndex()
    index.execute()

    return render_template('titles.j2', menu=menu, help=help, index=index)

@app.route('/words')
def words():
    menu = Page('MainMenu')
    help = Page('WordsHelp')

    index = WordIndex()
    index.execute()

    return render_template('words.j2', menu=menu, help=help, index=index)

@app.route('/changes')
def changes():
    menu = Page('MainMenu')
    help = Page('ChangesHelp')

    changes = Changes()
    changes.execute()

    return render_template('changes.j2', menu=menu, help=help, changes=changes)

@app.route('/search')
def search():
    menu = Page('MainMenu')
    help = Page('SearchHelp')

    query = request.args.get('query', '')
    fulltext = request.args.get('fulltext', False)

    search = Search(query, fulltext)

    if query:
        search.execute()

    return render_template('search.j2', menu=menu, help=help, search=search)

@app.route('/facets')
@app.route('/facets/<path:query>')
def facets(query=None):
    menu = Page('MainMenu')
    help = Page('FacetsHelp')

    facets = FacetsBrowser(query)
    facets.execute()

    return render_template('facets.j2', menu=menu, help=help, facets=facets)

# Functions to keep track of when people have changed pages, so we can
# do the recent changes page and so on.
# The editlog is stored with one record per line, as tab-separated
# words: page_name, host, time

def editlog_add(page_name, host):
    editlog = open(CHANGE_LOG, 'a+')
    try:
        editlog.seek(0, 2)                  # to end
        editlog.write("\t".join((page_name, host, `time()`)) + "\n")
    finally:
        editlog.close()

def editlog_raw_lines():
    editlog = open(CHANGE_LOG, 'rt')
    try:
        return editlog.readlines()
    finally:
        editlog.close()

def page_list():
    files = filter(WIKILINK_RE.match, os.listdir(DATA_DIR))
    files.sort()
    return files

def group_refinements(refinements):
    result = {}
    for kv in refinements:
        if result.has_key(kv.key):
            result[kv.key].append(kv)
        else:
            result[kv.key] = [kv]
    for key in result.keys():
        result[key].sort()
    return result

# raises ValueError on failure
def str_to_pair(str, separator):
    i = str.index(separator)
    return (str[0:i], str[i+len(separator):])

if __name__ == '__main__':
    app.run()
