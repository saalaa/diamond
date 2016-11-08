import re

from collections import OrderedDict
from jinja2 import Markup
from slugify import slugify
from diamond.app import app
from diamond.formatter import convert

WORD_PATTERN = r'[A-Z][a-z]+'

@app.template_filter('slug')
def slug(text):
    return slugify(text)

@app.template_filter('format')
def format(text):
    return Markup(convert(text))

@app.template_filter('letters')
def letters(items):
    letters = set()
    for item in items:
        letters.add(item[0].lower())

    return list(letters)

@app.template_filter('words')
def words(items):
    regexp = re.compile(WORD_PATTERN)

    words = {}
    for item in items:
        for word in regexp.findall(item):
            words.setdefault(word, []) \
                    .append(item)

    words = sorted(words.items(), key=lambda t: t[0])

    return OrderedDict(words)

@app.template_filter('title')
def title(title):
    title = re.sub('_', ' ', title)
    title = re.sub('([a-z])([A-Z])', r'\1 \2', title)

    return title

@app.template_filter('pluralize')
def pluralize(number, singular='', plural='s'):
    return (singular if number == 1 else plural) % number
