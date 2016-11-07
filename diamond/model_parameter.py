import time

from db import db

PARAMETER_DELAY = 300

def param(key, default='', cast=None):
    return Parameter.get(key, default, cast)

class Parameter(db.Model):
    __tablename__ = 'parameters'

    key = db.Column(db.String, primary_key=True)
    value = db.Column(db.String, nullable=False)

    cache = timestamp = None

    @classmethod
    def get_all(cls):
        items = Parameter.query \
                .all()

        values = {}
        for item in items:
            values[item.key] = item.value

        return values

    @classmethod
    def get(cls, key, default='', cast=None):
        now = time.time()

        if not cls.cache or cls.timestamp + PARAMETER_DELAY > now:
            cls.cache = cls.get_all()
            cls.timestamp = now

        value = cls.cache.get(key, default)

        if cast:
            value = cast(value)

        return value

    @classmethod
    def clear_cache(cls):
        cls.cache = None

    @classmethod
    def set(cls, key, value):
        items = Parameter.query \
                .filter(Parameter.key == key) \
                .all()

        for item in items:
            db.session.delete(item)

        Parameter(key=key, value=value) \
                .save()

    def save(self):
        db.session.add(self)
