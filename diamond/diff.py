import difflib

def markup_new(text):
    return '<span class="line-new">' + text + '</span>'

def markup_old(text):
    return '<span class="line-old">' + text + '</span>'

def markup_common(text):
    return '<span class="line-common">' + text + '</span>'

def markup_inline(text, markup):
    text = text.replace('\x00+', '<span class="chunk-added">')
    text = text.replace('\x00-', '<span class="chunk-deleted">')
    text = text.replace('\x00^', '<span class="chunk-changed">')
    text = text.replace('\x01', '</span>')

    return markup(text)

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
