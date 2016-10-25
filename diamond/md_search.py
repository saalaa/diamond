from markdown import Extension
from markdown.util import etree
from markdown.blockprocessors import BlockProcessor

class SearchProcessor(BlockProcessor):
    def test(self, parent, block):
        return block.startswith('@search')

    def run(self, parent, blocks):
        blocks.pop(0)

        div = etree.SubElement(parent, 'div')
        div.set('class', 'clear')

        form = etree.SubElement(div, 'form')
        form.set('action', '/search')

        left_col = etree.SubElement(form, 'div')
        left_col.set('class', 'col-7 col-9-m no-padding')

        right_col = etree.SubElement(form, 'div')
        right_col.set('class', 'col-5 col-3-m no-padding')

        fulltext = etree.SubElement(left_col, 'input')
        fulltext.set('type', 'hidden')
        fulltext.set('name', 'fulltext')
        fulltext.set('value', 'yes')

        query = etree.SubElement(left_col, 'input')
        query.set('type', 'text')
        query.set('name', 'query')
        query.set('class', 'field')

        button = etree.SubElement(right_col, 'button')
        button.set('type', 'submit')
        button.set('class', 'button button-fw no-padding')
        button.text = 'Go!'

class SearchExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.parser.blockprocessors.add('search', SearchProcessor(md.parser),
                '_begin')
