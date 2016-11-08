import markdown

from markdown.extensions.codehilite import CodeHiliteExtension
from diamond.formatter.link import LinkExtension
from diamond.formatter.list import ListExtension
from diamond.formatter.redirect import RedirectExtension
from diamond.formatter.search import SearchExtension
from diamond.formatter.title import TitleExtension

def convert(text):
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.meta',
        LinkExtension(),
        ListExtension(),
        RedirectExtension(),
        SearchExtension(),
        CodeHiliteExtension(guess_lang=False)
    ])

    return md.convert(text)

def parse(text):
    md = markdown.Markdown(extensions=[
        'markdown.extensions.meta',
        RedirectExtension(),
        TitleExtension()
    ])

    md.convert(text)

    return {
        'title': getattr(md, 'Title', ''),
        'meta': getattr(md, 'Meta', {}),
        'redirect': getattr(md, 'Redirect', {})
    }
