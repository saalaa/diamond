import re

from random import random
from slugify import slugify
from markdown.extensions.wikilinks import WikiLinkExtension, WikiLinks

LINK_PATTERN = r'\[\[([\w0-9\?\!\(\)\'_ -]+)\]\]'

def build_url(label, base, end):
    return '/%s' % slugify(label)

class LinkExtension(WikiLinkExtension):
    def __init__(self, *args, **kwargs):
        self.config = {
            'base_url': ['/', 'String to append to beginning or URL.'],
            'end_url': ['', 'String to append to end of URL.'],
            'html_class': ['wikilink', 'CSS hook. Leave blank for none.'],
            'build_url': [build_url, 'Callable formats URL from label.'],
        }

    def extendMarkdown(self, md, md_globals):
        wikilinkPattern = WikiLinks(LINK_PATTERN, self.getConfigs())
        wikilinkPattern.md = md

        md.inlinePatterns.add('wikilink', wikilinkPattern, '<not_strong')
