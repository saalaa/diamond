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

from markdown import Markdown
from diamond.formatter.title import TitleExtension

def test_title_ext():
    extension = TitleExtension()
    markdown = Markdown(extensions=[extension])

    html = markdown.convert('')

    assert not hasattr(markdown, 'Title')
    assert getattr(markdown, 'Title', 'xxx') == 'xxx'

    html = markdown.convert('# yyy')

    assert 'yyy' in html

    assert hasattr(markdown, 'Title')
    assert getattr(markdown, 'Title', 'zzz') == 'yyy'
