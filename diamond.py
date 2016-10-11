#! /usr/bin/env python2.2

"""Quick-quick implementation of WikiWikiWeb in Python
"""

# Copyright (C) 1999, 2000 Martin Pool <mbp@humbug.org.au>
# Copyright (C) 2003 Kimberley Burchett http://www.kimbly.com/

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

__version__ = '0.2';


import cgi, sys, string, os, re, errno, time, stat, urllib
from cgi import log
from os import path, environ
from socket import gethostbyaddr
from time import localtime, strftime
from cStringIO import StringIO

True = 1
False = 0

def emit_header():
    print "Content-type: text/html"
    print


# Regular expression defining a WikiWord (but this definition
# is also assumed in other places.
word_re_str = r"\b([A-Z][a-z]+){2,}\b"
word_anchored_re = re.compile('^' + word_re_str + '$')
command_re_str = "(search|edit|fullsearch|titlesearch)\=(.*)"

# Editlog -----------------------------------------------------------

# Functions to keep track of when people have changed pages, so we can
# do the recent changes page and so on.
# The editlog is stored with one record per line, as tab-separated
# words: page_name, host, time

# TODO: Check values written in are reasonable

def editlog_add(page_name, host):
    editlog = open(editlog_name, 'a+')
    try: 
        # fcntl.flock(editlog.fileno(), fcntl.LOCK_EX)
        editlog.seek(0, 2)                  # to end
        editlog.write(string.join((page_name,host,`time.time()`), "\t") + "\n")
    finally:
        # fcntl.flock(editlog.fileno(), fcntl.LOCK_UN)
        editlog.close()


def editlog_raw_lines():
    editlog = open(editlog_name, 'rt')
    try:
        # fcntl.flock(editlog.fileno(), fcntl.LOCK_SH)
        return editlog.readlines()
    finally:
        # fcntl.flock(editlog.fileno(), fcntl.LOCK_UN)
        editlog.close()




# Formatting stuff --------------------------------------------------


def get_scriptname():
    return environ.get('SCRIPT_NAME', '')


def send_title(text, link=None, msg=None):
    print "<head><title>%s</title>" % text
    print """<style type="text/css">
    .body {
        font: 10pt/15pt arial;
        background-color: #FFFFFF; 
        color: #000000;
    }
    a {
        font-weight: bold; 
        color: #7050c0;
        text-decoration: none;
    }
    a:hover, a:active {
        text-decoration: underline;
        color: #5080a0;
    }
    a.nonexistent {
        vertical-align: top;
    }
    .title, .title a, .title a:hover, .title a:active {
        font: normal 24pt georgia; 
        letter-spacing: 1px;
        color: #000000;
    }
    .metabox {
        background-color: #d8d8f4;
    }
    .metakey {
        background-color: #e8e8f4;
        font: normal 10pt/11pt arial;
    }
    .metaval {
        background-color: #ffffff;
        font: normal 10pt/11pt arial;
    }
    </style>"""
    print "</head>"
    print '<body class="body" bgcolor="#ffffff" text="#000000" link="#4040ff vlink="#4040ff>'
    print '<table><tr><td valign=absmiddle>'
    print '<a href="%s">%s</a>' % (get_scriptname()+"/BrowseFacets/", logo_string)
    print '</td>'
    print '<td width=10></td>'
    print '<td><h1 class="title">'
    if link:
        print '<a href="%s">%s</a>' % (link, text)
    else:
        print text
    print '</h1></td></table><p>'
    if msg: print msg, "<hr>"



def link_tag(params, text=None, ss_class=None):
    if text is None:
        text = params                   # default
    if ss_class:
        classattr = 'class="%s" ' % ss_class
    else:
        classattr = ''
    return '<a %s href="%s/%s">%s</a>' % (classattr, get_scriptname(),
                                         params, text)


def send_unordered_list(list):
    print "<UL>"
    for item in list:
        print '<LI>' + item
    print "</UL>"



# Search ---------------------------------------------------

def do_fullsearch(needle):
    send_title('Full text search for "%s"' % (needle))

    needle_re = re.compile(needle, re.IGNORECASE)
    hits = []
    all_pages = page_list()
    for page_name in all_pages:
        body = Page(page_name).get_body()
        count = len(needle_re.findall(body))
        if count:
            hits.append((count, page_name))

    # The default comparison for tuples compares elements in order,
    # so this sorts by number of hits
    hits.sort()
    hits.reverse()

    print "<span class='body nav'>"
    print "<UL>"
    for (count, page_name) in hits:
        print '<LI>' + Page(page_name).link_to()
        print ' . . . . ' + `count`
        print ['match', 'matches'][count != 1]
    print "</UL>"
    print "</span>"

    print_search_stats(len(hits), len(all_pages))


def do_browse(view):
    if (view.breadcrumb()):
        send_title("Browsing "+view.breadcrumb())
    else:
        send_title("Browsing All Pages")

    all_pages = page_list()
    hits = view.pages()

    refinements = view.refinements(hits)
    groups = group_refinements(refinements)

    print "<table class='body nav'><tr><td valign=top>"

    group_names = groups.keys()
    group_names.sort()
    first = True
    for group_name in group_names:
        if not first: print "<br>"
        first = False
        print "<b>%s</b><br>" % group_name
        for kv in groups[group_name]:
            subview = View().copy(view).narrow(kv)
            print "&nbsp;&nbsp;%s <small>(%s)</small><br>" % \
                (subview.link_to(kv.val), kv.count)
        none_view = View().copy(view).narrow(KeyVal(group_name, ""))
        none_view_pages = none_view.pages()
        if none_view_pages:
            print "&nbsp;&nbsp;%s <small>(%s)</small><br>" % \
                (none_view.link_to("&lt;none&gt;"), len(none_view_pages))

    print "</td><td width=30>"
    print "</td><td valign='top'>"

    print "<p><b>%d pages" % len(hits)
    if len(all_pages) == len(hits):
        print "</b>"
    else:
        print " (out of %s)</b>\n" % View().link_to(len(all_pages))

    send_unordered_list([p.link_to() for p in hits])

    print "</td></tr></table>"


def do_titlesearch(needle):
    # TODO: check needle is legal -- but probably we can just accept any RE

    send_title("Title search for \"" + needle + '"')
    
    needle_re = re.compile(needle, re.IGNORECASE)
    all_pages = page_list()
    hits = filter(needle_re.search, all_pages)

    print "<span class='body nav'>"
    send_unordered_list([Page(file).link_to() for file in hits])
    print "</span>"

    print_search_stats(len(hits), len(all_pages))


def print_search_stats(hits, searched):
    print "<p>%d hits " % hits
    print " out of %d pages searched." % searched


def do_edit(pagename):
    Page(pagename).send_editor()


def do_savepage(pagename):
    global form
    pg = Page(pagename)
    newtext = ""
    newmeta = ""
    if form.has_key('savetext'):
        newtext = form['savetext'].value
    if form.has_key('savemeta'):
        newmeta = form['savemeta'].value

    if looks_like_spam(newtext + newmeta):
        msg = "<i>Sorry, your changes look like spam.  Spam is illegal.  " \
              "Your changes have been ignored, and your IP address has been " \
              "logged for potential legal action.</i>"
    else:
        pg.save_text(newtext)
        pg.save_metadata(newmeta)
        msg = """<i>Thank you for your changes.  Your attention to
                 detail is appreciated.</i>"""
    pg.send_page(msg=msg)


def make_index_key():
    s = '<p><center>'
    links = map(lambda ch: '<a href="#%s">%s</a>' % (ch, ch),
                string.lowercase)
    s = s + string.join(links, ' | ')
    s = s + '</center><p>'
    return s


def page_list():
    files = filter(word_anchored_re.match, os.listdir(text_dir))
    files.sort()
    return files


def print_footer(name, editable=True, mod_string=None):
    base = get_scriptname()
    print '<hr noshade size=1>'
    if editable:
        print link_tag('?edit='+name, 'EditText')
        #if mod_string:
            #print "(last modified %s)" % mod_string
    print "|", link_tag('BrowseFacets', 'BrowseFacets')
    print "|", link_tag('RecentChanges', 'RecentChanges')
    print "|", link_tag('FindPage?value='+name, 'FindPage')


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
    i = string.index(str, separator)
    return (str[0:i], str[i+len(separator):])
    

def looks_like_spam(text):
    keywords = open(data_dir + "spam_keywords", "r")
    for keyword in keywords:
        keyword = keyword.rstrip("\r\n\t ").strip(" \t")
        if text.find(keyword) <> -1:
            return True
    return False



# ----------------------------------------------------------
# Macros
def _macro_TitleSearch():
    return _macro_search("titlesearch")

def _macro_FullSearch():
    return _macro_search("fullsearch")

def _macro_search(type):
    if form.has_key('value'):
        default = form["value"].value
    else:
        default = ''
    return """<form method=get>
    <input name=%s size=30 value="%s"> 
    <input type=submit value="Go">
    </form>""" % (type, default)

def _macro_GoTo():
    return """<form method=get><input name=goto size=30>
    <input type=submit value="Go">
    </form>"""
    # isindex is deprecated, but it gives the right result here

def _macro_WordIndex():
    s = make_index_key()
    pages = list(page_list())
    map = {}
    word_re = re.compile('[A-Z][a-z]+')
    for name in pages:
        for word in word_re.findall(name):
            try:
                map[word].append(name)
            except KeyError:
                map[word] = [name]

    all_words = map.keys()
    all_words.sort()
    last_letter = None
    for word in all_words:
        letter = string.lower(word[0])
        if letter != last_letter:
            s = s + '<a name="%s"></a><h3>%s</h3>\n' % (letter, letter)
            last_letter = letter
            
        s = s + '<b>%s</b><br>\n' % word
        links = map[word]
        links.sort()
        last_page = None
        for name in links:
            if name == last_page: continue
            s = s + '&nbsp;'*5 + Page(name).link_to() + "<br>\n"
    return s


def _macro_TitleIndex():
    s = make_index_key()
    pages = list(page_list())
    pages.sort()
    current_letter = None
    for name in pages:
        letter = string.lower(name[0])
        if letter != current_letter:
            s = s + '<a name="%s"></a><h3>%s</h3>\n' % (letter, letter)
            current_letter = letter
        else:
            s = s + '<br>\n'
        s = s + Page(name).link_to()
    return s


def _macro_RecentChanges():
    lines = editlog_raw_lines()
    lines.reverse()
    
    ratchet_day = None
    done_words = {}
    buf = StringIO()
    for line in lines:
        page_name, addr, ed_time = line.split('\t')
        # year, month, day, DoW
        time_tuple = localtime(float(ed_time) - 4*60*60)
        day = tuple(time_tuple[0:3])

        if done_words.has_key(page_name):
            continue

        if day != ratchet_day:
            buf.write('</table>\n')
            buf.write('\n<h3>%s</h3>\n\n' % strftime(date_fmt, time_tuple))
            buf.write('<table class="body nav" width="100%">\n')
            ratchet_day = day

        done_words[page_name] = True
        buf.write('<tr><td width="35%">')
        buf.write(Page(page_name).link_to())
        if changed_time_fmt:
            buf.write('</td><td>')
            buf.write(time.strftime(changed_time_fmt, time_tuple))
        buf.write('</td></tr>\n')
    buf.write('</table>\n')

    return buf.getvalue()



# ----------------------------------------------------------
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


    def describe_val(self):
        return self.val or "No "+self.key

    def url_piece(self):
        return "/%s=%s" % (urllib.quote(self.key), urllib.quote(self.val))


# ----------------------------------------------------------
class View:
    """A view is the subset of pages that match particular metadata 
    key-value pairs.  In fact, it's just the key/value pairs, and the 
    pages are handled separately"""

    def __init__(self):
        # note that keyvals is a list, not a dictionary.  This is because
        # we want to support multi-assignment (e.g. "Subject=foo" and 
        # "Subject=bar").  Also, we want to preserve order for breadcrumbs.
        self.keyvals = []


    def copy(self, other_view):
        self.keyvals = [keyval for keyval in other_view.keyvals]
        return self

    def from_url(self, url):
        self.keyvals = []
        for chunk in url.split("/"):
            try:
		(key, val) = str_to_pair(chunk, "=")
                self.narrow(KeyVal(key, val))
            except ValueError, er:
                pass
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


    def breadcrumb(self):
        crumbs = [kv.describe_val() for kv in self.keyvals]
        return string.join(crumbs, ", ")


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


    def link_to(self, title):
        url = ""
        for kv in self.keyvals:
            url += kv.url_piece()
        return "<A HREF='%s/BrowseFacets%s'>%s</A>" % \
                (get_scriptname(), url, title)


    def to_string(self):
        result = ""
        for kv in self.keyvals:
            if len(result): result += ", "
            result += kv.key + ":" + kv.val
        return result


# ----------------------------------------------------------
class PageFormatter:
    """Object that turns Wiki markup into HTML.

    All formatting commands can be parsed one line at a time, though
    some state is carried over between lines.
    """
    def __init__(self, raw_body):
        self.raw_body = raw_body
        self.is_em = self.is_b = 0
        self.list_indents = []
        self.in_pre = 0


    def _emph_repl(self, word):
        if len(word) == 3:
            self.is_b = not self.is_b
            return ['</b>', '<b>'][self.is_b]
        else:
            self.is_em = not self.is_em
            return ['</em>', '<em>'][self.is_em]

    def _rule_repl(self, word):
        s = self._undent()
        width = (len(word) - 3) * 25;
        if width < 0: width = 25
        if width > 100: width = 100
        s = s + "\n<hr noshade size=1 width='%s%%'>\n" % (width)
        return s

    def _word_repl(self, word):
        return Page(word).link_to()


    def _url_repl(self, word):
        return '<a href="%s">%s</a>' % (word, word)


    def _email_repl(self, word):
        return '<a href="mailto:%s">%s</a>' % (word, word)


    def _ent_repl(self, s):
        return {'&': '&amp;',
                '<': '&lt;',
                '>': '&gt;'}[s]
    

    def _li_repl(self, match):
        return '<li>'


    def _pre_repl(self, word):
        if word == '{{{' and not self.in_pre:
            self.in_pre = True
            return '<pre>'
        elif self.in_pre:
            self.in_pre = False
            return '</pre>'
        else:
            return ''

    def _macro_repl(self, word):
        macro_name = word[2:-2]
        # TODO: Somehow get the default value into the search field
        return apply(globals()['_macro_' + macro_name], ())


    def _indent_level(self):
        return len(self.list_indents) and self.list_indents[-1]

    def _indent_to(self, new_level):
        s = ''
        while self._indent_level() > new_level:
            del(self.list_indents[-1])
            s = s + '</ul>\n'
        while self._indent_level() < new_level:
            self.list_indents.append(new_level)
            s = s + '<ul>\n'
        return s

    def _undent(self):
        res = '</ul>' * len(self.list_indents)
        self.list_indents = []
        return res


    def replace(self, match):
        for type, hit in match.groupdict().items():
            if hit:
                return apply(getattr(self, '_' + type + '_repl'), (hit,))
        else:
            raise "Can't handle match " + `match`
        

    def print_html(self):
        # For each line, we scan through looking for magic
        # strings, outputting verbatim any intervening text
        scan_re = re.compile(
            r"(?:(?P<emph>'{2,3})"
            + r"|(?P<ent>[<>&])"
            + r"|(?P<word>\b(?:[A-Z][a-z]+){2,}\b)"
            + r"|(?P<rule>-{4,})"
            + r"|(?P<url>(http|ftp|nntp|news|mailto)\:[^\s'\"]+\S)"
            + r"|(?P<email>[-\w._+]+\@[\w.-]+)"
            + r"|(?P<li>^\s+\*)"
            + r"|(?P<pre>(\{\{\{|\}\}\}))"
            + r"|(?P<macro>\[\[(TitleSearch|FullSearch|WordIndex"
                            + r"|TitleIndex|RecentChanges|GoTo)\]\])"
            + r")")
        blank_re = re.compile("^\s*$")
        bullet_re = re.compile("^\s+\*")
        indent_re = re.compile("^\s*")
        eol_re = re.compile(r'\r?\n')
        raw_body = string.expandtabs(self.raw_body)
        for line in eol_re.split(raw_body):
            if not self.in_pre:
                # XXX: Should we check these conditions in this order?
                if blank_re.match(line):
                    print '<p>'
                    continue
                indent = indent_re.match(line)
                print self._indent_to(len(indent.group(0)))
            print re.sub(scan_re, self.replace, line)
        if self.in_pre: print '</pre>'
        print self._undent()
        

# ----------------------------------------------------------
class Page:
    def __init__(self, page_name):
        self.page_name = page_name

    def split_title(self):
        # look for the end of words and the start of a new word,
        # and insert a space there
        return re.sub('([a-z])([A-Z])', r'\1 \2', self.page_name)


    def _body_filename(self):
        return path.join(text_dir, self.page_name)

    def _metadata_filename(self):
        return path.join(text_dir, self.page_name + ".meta")


    def _tmp_filename(self):
        return path.join(text_dir, ('#' + self.page_name + '.' + `os.getpid()` + '#'))


    def exists(self):
        try:
            os.stat(self._body_filename())
            return True
        except OSError, er:
            if er.errno == errno.ENOENT:
                return False
            else:
                raise er
        

    def link_to(self):
        word = self.page_name
        if self.exists():
            return link_tag(word)
        else:
            return word + link_tag(word, '*', 'nonexistent')


    def raw_metadata(self):
        try:
            metatext = open(self._metadata_filename(), 'rt').read()
	    return metatext or 'Enter meta data here.'
        except IOError, er:
            if er.errno == errno.ENOENT:
                # just doesn't exist, use default
                return 'Enter meta data here.'
            else:
                raise er

    def metadata(self):
        metatext = self.raw_metadata()
        metatext = string.replace(metatext, "\r\n", "\n")
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
                return 'Describe %s here.' % self.page_name
            else:
                raise er
    

    def send_page(self, msg=None):
        link = get_scriptname() + '?fullsearch=' + self.page_name
        send_title(self.split_title(), link, msg)
        PageFormatter(self.get_body()).print_html()

        # kbkb -- move this to a method somewhere
        if not self.metadata().is_empty():
            print "<p><table class='body metabox'>\n"
            
        for kv in self.metadata().keyvals:
            print "<tr>"
            print "<td class='metakey'>%s: </td> " % (kv.key)
            val_link = View().narrow(kv).link_to(kv.val)
            print "<td class='metaval'> %s</td>" % (val_link)
            print "</tr>\n"

        if not self.metadata().is_empty():
            print "</table>\n"

        print_footer(self.page_name, True, self._last_modified())


    def _last_modified(self):
        if not self.exists():
            return None
        modtime = localtime(os.stat(self._body_filename())[stat.ST_MTIME])
        return strftime(datetime_fmt, modtime)


    def send_editor(self):
        send_title('Edit ' + self.split_title())
        print '<form method="post" action="%s">' % (get_scriptname())
        print '<input type=hidden name="savepage" value="%s">' % (self.page_name)
        body = string.replace(self.get_body(), '\r\n', '\n')
        meta = string.replace(self.raw_metadata(), '\r\n', '\n')
        print """<textarea wrap="virtual" name="savetext" rows="17"
                 cols="80">%s</textarea><br>""" % body
        print """<textarea wrap="virtual" name="savemeta" rows="4"
                 cols="80">%s</textarea>""" % meta
        print """<br><input type=submit value="Save">
                 <input type=reset value="Reset">
                 """
        print "</form>"
        print "<p>" + Page('EditingTips').link_to()
                 

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


    def save_text(self, newtext):
        self._write_file(newtext, self._body_filename())
        remote_name = environ.get('REMOTE_ADDR', '')
        editlog_add(self.page_name, remote_name)
        
    def save_metadata(self, newmetatext):
        self._write_file(newmetatext, self._metadata_filename())
        remote_name = environ.get('REMOTE_ADDR', '')
        editlog_add(self.page_name, remote_name)
        

emit_header()

# Configurable parts ------------------------------------------
data_dir = 'data/'
text_dir = path.join(data_dir, 'text')
editlog_name = path.join(data_dir, 'editlog')
cgi.logfile = path.join(data_dir, 'cgi_log')
logo_string = """<img style="vertical-align: middle" 
                      src="/diamond.jpg" 
                      border=0 
                      alt="diamond logo">"""
changed_time_fmt = '%I:%M&nbsp;%P'
date_fmt = '%A, %d %B %Y'
datetime_fmt = '%a %d %b %Y %I:%M %p'
css_url = '/piki-data/piki.css'         # stylesheet link, or ''

try:
    form = cgi.FieldStorage()

    handlers = { 'fullsearch':  do_fullsearch,
                 'titlesearch': do_titlesearch,
                 'edit':        do_edit,
                 'savepage':    do_savepage }

    for cmd in handlers.keys():
        if form.has_key(cmd):
            apply(handlers[cmd], (form[cmd].value,))
            break
    else:
        path_info = environ.get('PATH_INFO', '')

        if form.has_key('goto'):
            query = form['goto'].value
        elif len(path_info) and path_info[0] == '/':
            query = path_info[1:] or 'FrontPage'
        else:       
            query = environ.get('QUERY_STRING', '') or 'FrontPage'

        word_match = re.match(word_re_str, query)
        if path_info.startswith("/BrowseFacets/") or path_info=="/BrowseFacets":
            do_browse(View().from_url(path_info[13:]))
        elif word_match:
            word = word_match.group(0)
            Page(word).send_page()
        else:
            print "<p>Can't work out query \"<pre>" + query + "</pre>\""

except:
    cgi.print_exception()

sys.stdout.flush()
