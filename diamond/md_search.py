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
