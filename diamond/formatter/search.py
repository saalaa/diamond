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

from markdown import Extension
from markdown.util import etree
from markdown.blockprocessors import BlockProcessor

class SearchProcessor(BlockProcessor):
    def test(self, parent, block):
        return block.startswith('@search')

    def run(self, parent, blocks):
        blocks.pop(0)

        div = etree.SubElement(parent, 'div')
        div.set('class', 'search')

        link = etree.SubElement(div, 'a')
        link.set('href', '/search')
        link.set('class', 'hidden-l wikilink')
        link.text = 'Search'

        form = etree.SubElement(div, 'form')
        form.set('action', '/search')
        form.set('class', 'hidden visible-l')

        query = etree.SubElement(form, 'input')
        query.set('type', 'text')
        query.set('name', 'query')

        button = etree.SubElement(form, 'button')
        button.set('type', 'submit')
        button.text = 'Search'

class SearchExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.parser.blockprocessors.add('search', SearchProcessor(md.parser),
                '_begin')
