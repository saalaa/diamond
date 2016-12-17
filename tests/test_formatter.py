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

import pytest

from markdown import Markdown
from diamond.cli import drop_db, init_db, load_fixtures
from diamond.formatter import convert, parse
from diamond.formatter.link import LinkExtension
from diamond.formatter.list import ListExtension
from diamond.formatter.redirect import RedirectExtension
from diamond.formatter.search import SearchExtension
from diamond.formatter.title import TitleExtension

FIXTURE = '''
---
aaa: 1
bbb: 2
---

# xxx

@search

@redirect { "page": "yyy" }

@list {}

@list { "raw": 1 }

@list { "filters": { "category": "iii" } }

Clerkless lofting [oblivionize Anastasian] inconglomerate Mohock [[Cntrophore
merocerite]] teledendrion dandruffy [[Pygopus falsidical!]] autopelagic
suspiratious [[Counterorganization[peripherical]] pout lateroversion [[cursed

San]]
'''.strip()


@pytest.fixture
def database():
    drop_db()
    init_db()
    load_fixtures()


def test_title_convert(database):
    assert convert('') == ''

    html = convert(FIXTURE)

    assert html

    assert 'aaa' not in html
    assert 'bbb' not in html

    assert 'xxx' in html

    assert '@redirect' in html
    assert '@search' not in html
    assert '@list' not in html

    assert '<h1' in html
    assert '<li' in html
    assert '<input' in html

    # 1 @search, 1 link and 4x2 @list
    assert html.count('href=') == 10


def test_title_parse():
    data = parse('')

    assert 'title' in data
    assert 'meta' in data
    assert 'redirect' in data

    data = parse(FIXTURE)

    assert data['title'] == 'xxx'
    assert data['redirect'] == {'page': 'yyy'}
    assert data['meta']['aaa'] == ['1']
    assert data['meta']['bbb'] == ['2']


def test_title_link():
    extension = LinkExtension()
    markdown = Markdown(extensions=[extension])

    assert markdown.convert('') == ''

    html = markdown.convert(FIXTURE)

    assert 'oblivionize Anastasian' in html
    assert 'oblivionize-anastasian' not in html

    assert 'Cntrophore' in html
    assert 'merocerite' in html
    assert 'cntrophore-merocerite' not in html

    assert 'Pygopus falsidical!' in html
    assert 'pygopus-falsidical' in html

    assert 'Counterorganization[peripherical' in html
    assert 'counterorganization-peripherical' not in html

    assert 'cursed' in html
    assert 'San' in html

    assert 'cursed San' not in html
    assert 'cursed-san' not in html


def test_title_list(database):
    extension = ListExtension()
    markdown = Markdown(extensions=[extension])

    assert markdown.convert('') == ''

    html = markdown.convert(FIXTURE)

    assert '@list' not in html
    assert '<li' in html


def test_title_redirect():
    extension = RedirectExtension()
    markdown = Markdown(extensions=[extension])

    assert markdown.convert('') == ''

    assert not hasattr(markdown, 'Redirect')
    assert getattr(markdown, 'Redirect', {}) == {}

    html = markdown.convert(FIXTURE)

    assert 'redirect' in html

    assert hasattr(markdown, 'Redirect')
    assert getattr(markdown, 'Redirect', {}) == {'page': 'yyy'}


def test_title_search():
    extension = SearchExtension()
    markdown = Markdown(extensions=[extension])

    assert markdown.convert('') == ''

    html = markdown.convert(FIXTURE)

    assert '<input' in html
    assert '@search' not in html


def test_title_ext():
    extension = TitleExtension()
    markdown = Markdown(extensions=[extension])

    assert markdown.convert('') == ''

    assert not hasattr(markdown, 'Title')
    assert getattr(markdown, 'Title', 'zzz') == 'zzz'

    html = markdown.convert(FIXTURE)

    assert 'xxx' in html

    assert hasattr(markdown, 'Title')
    assert getattr(markdown, 'Title', 'zzz') == 'xxx'
