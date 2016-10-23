import markdown

from markdown.extensions.wikilinks import WikiLinkExtension, WikiLinks
from markdown.extensions.codehilite import CodeHiliteExtension

WIKILINK_PATTERN = r'\[\[([\w0-9\(\)\'_ -]+)\]\]'

class ExtendedWikiLinkExtension(WikiLinkExtension):
    def extendMarkdown(self, md, md_globals):
        self.md = md

        wikilinkPattern = WikiLinks(WIKILINK_PATTERN, self.getConfigs())
        wikilinkPattern.md = md

        md.inlinePatterns.add('wikilink', wikilinkPattern, '<not_strong')

def convert(text):
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.meta',
        'markdown.extensions.toc',
        CodeHiliteExtension(guess_lang=False),
        ExtendedWikiLinkExtension(end_url='')
    ])

    return md.convert(text)

def parse(text):
    md = markdown.Markdown(extensions=['markdown.extensions.meta'])
    md.convert(text)

    return getattr(md, 'Meta', {})
