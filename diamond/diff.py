import difflib

from markupsafe import Markup, escape

def markup_new(text):
    return Markup('<span class="line-new">') + escape(text) + Markup('</span>')

def markup_old(text):
    return Markup('<span class="line-old">') + escape(text) + Markup('</span>')

def markup_common(text):
    return escape(text)

def markup_inline(text, markup):
    return markup(text) \
            .replace('\x00+', Markup('<span class="chunk-added">')) \
            .replace('\x00-', Markup('<span class="chunk-deleted">')) \
            .replace('\x00^', Markup('<span class="chunk-changed">')) \
            .replace('\x01', Markup('</span>'))

def unified_diff(a, b, name_a, name_b):
    yield markup_old(name_a)
    yield markup_new(name_b)

    yield ''

    for old, new, changed in difflib._mdiff(a, b):
        if changed:
            if not old[0]:
                yield markup_new(new[1][2:])
            elif not new[0]:
                yield markup_old(old[1][2:])
            else:
                yield markup_inline(old[1], markup_old)
                yield markup_inline(new[1], markup_new)
        else:
            yield markup_common(old[1])
