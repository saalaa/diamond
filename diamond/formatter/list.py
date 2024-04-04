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

from markdown import Extension
from markdown.blockprocessors import BlockProcessor
from diamond.models import Document


class ListProcessor(BlockProcessor):
    def test(self, parent, block):
        return block.startswith('@list')

    def run(self, parent, blocks):
        block = blocks.pop(0)

        (directive, rest) = block.split(' ', 1)

        config = json.loads(rest)

        raw = config.get('raw', False)
        filters = config.get('filters')

        if filters:
            filters = filters.items()

        items = Document.search(filters=filters)

        if items:
            if raw:
                items = ['- [[' + item.slug + ']]' for item in items]
            else:
                items = ['- [' + item.title + '](' + item.slug + ')'
                            for item in items]
        else:
            items = ['- *No results found*']

        blocks.insert(0, '\n'.join(items))


class ListExtension(Extension):
    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.parser.blockprocessors.register(ListProcessor(md.parser), 'list', 100)
