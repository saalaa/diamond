import markdown

from slugify import slugify

from markdown import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.extensions.wikilinks import WikiLinkExtension, WikiLinks
from markdown.extensions.codehilite import CodeHiliteExtension

WIKILINK_PATTERN = r'\[\[([\w0-9\(\)\'_ -]+)\]\]'

def build_url(label, base, end):
    return '%s%s%s' % (base, slugify(label), end)

class ExtendedWikiLinkExtension(WikiLinkExtension):
    def extendMarkdown(self, md, md_globals):
        self.md = md

        wikilinkPattern = WikiLinks(WIKILINK_PATTERN, self.getConfigs())
        wikilinkPattern.md = md

        md.inlinePatterns.add('wikilink', wikilinkPattern, '<not_strong')

class TitleTreeProcessor(Treeprocessor):
    def __init__(self, md):
        self.md = md

    def run(self, root):
        for child in root.getchildren():
            if child.tag == 'h1':
                self.md.Title = (child.text or '').strip()
                break

class TitleExtension(Extension):
    TreeProcessorClass = TitleTreeProcessor

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)

        ext = self.TreeProcessorClass(md)

        self.md = md
        self.reset()

        md.treeprocessors.add('title', ext, '_end')

    def reset(self):
        self.md.Title = ''

def convert(text):
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.meta',
        CodeHiliteExtension(guess_lang=False),
        ExtendedWikiLinkExtension(end_url='', build_url=build_url)
    ])

    return md.convert(text)

def parse(text):
    md = markdown.Markdown(extensions=['markdown.extensions.meta',
        TitleExtension(),])

    md.convert(text)

    return {
        'title': getattr(md, 'Title', ''),
        'meta': getattr(md, 'Meta', {})
    }
