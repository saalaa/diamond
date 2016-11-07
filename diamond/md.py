import markdown

from markdown.extensions.codehilite import CodeHiliteExtension

from md_link import LinkExtension
from md_list import ListExtension
from md_redirect import RedirectExtension
from md_search import SearchExtension
from md_title import TitleExtension

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
