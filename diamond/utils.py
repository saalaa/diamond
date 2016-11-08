import os
import random

from werkzeug.utils import cached_property

DEFAULT_DOMAIN = [chr(i) for i in range(32, 127)]

def env(variable, default=None, cast=None):
    value = os.environ.get(variable, default)

    if cast:
        value = cast(value)

    return value

def secret(size=42, domain=DEFAULT_DOMAIN):
    return ''.join(random.sample(domain, size))
