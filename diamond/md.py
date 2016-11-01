import markdown

from markdown.extensions.codehilite import CodeHiliteExtension

from md_redirect import RedirectExtension
from md_title import TitleExtension
from md_link import LinkExtension
from md_list import ListExtension

def convert(text):
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.meta',
        RedirectExtension(),
        LinkExtension(),
        ListExtension(),
        CodeHiliteExtension(guess_lang=False)
    ])

    return md.convert(text)

def parse(text):
    md = markdown.Markdown(extensions=[
        'markdown.extensions.meta',
        TitleExtension(),
        RedirectExtension()
    ])

    md.convert(text)

    return {
        'title': getattr(md, 'Title', ''),
        'meta': getattr(md, 'Meta', {}),
        'redirect': getattr(md, 'Redirect', {})
    }
