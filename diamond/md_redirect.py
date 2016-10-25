import json

from markdown import Extension
from markdown.blockprocessors import BlockProcessor

class RedirectProcessor(BlockProcessor):
    def __init__(self, md, parser):
        self.md = md

        super(RedirectProcessor, self).__init__(parser)

    def test(self, parent, block):
        return block.startswith('@redirect')

    def run(self, parent, blocks):
        block = blocks.pop(0)

        (directive, rest) = block.split(' ', 1)

        self.md.Redirect = json.loads(rest)

        blocks.insert(0, '    ' + block)

class RedirectExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.parser.blockprocessors.add('redirect', RedirectProcessor(md,
            md.parser), '_begin')
