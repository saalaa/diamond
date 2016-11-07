import json

from model_document import Document
from markdown import Extension
from markdown.blockprocessors import BlockProcessor

class ListProcessor(BlockProcessor):
    def test(self, parent, block):
        return block.startswith('@list')

    def run(self, parent, blocks):
        block = blocks.pop(0)

        (directive, rest) = block.split(' ', 1)

        config = json.loads(rest)

        raw = config.get('raw', False)
        filters = config.get('filters')

        if config:
            filters = filters.items()

        items = Document.search(filters=filters)

        if items:
            if raw:
                items = ['- [[' + item.name + ']]' for item in items]
            else:
                items = ['- [' + item.title + '](' + item.name + ')'
                            for item in items]
        else:
            items = ['- *No results found*']

        blocks.insert(0, '\n'.join(items))

class ListExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.parser.blockprocessors.add('list', ListProcessor( md.parser),
                '_begin')
