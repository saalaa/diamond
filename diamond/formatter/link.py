# Copyright (C) 1999, 2000 Martin Pool <mbp@humbug.org.au>
# Copyright (C) 2003 Kimberley Burchett <http://www.kimbly.com>
# Copyright (C) 2016 Benoit Myard <myardbenoit@gmail.com>
#
# This file is part of Diamond wiki.
#
# Diamond wiki is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Diamond wiki is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Diamond wiki. If not, see <http://www.gnu.org/licenses/>.

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
