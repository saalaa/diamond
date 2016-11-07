from db import db

class Metadata(db.Model):
    __tablename__ = 'metadata'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    key = db.Column(db.String, nullable=False)
    value = db.Column(db.String, nullable=False)

    @classmethod
    def get(self, name):
        return Metadata.query \
                .filter(Metadata.name == name) \
                .order_by(Metadata.key, Metadata.value) \
                .all()

    @classmethod
    def search(self, key, value):
        items = db.session.query(Metadata.name) \
                .filter(Metadata.key == key) \
                .filter(Metadata.value == value) \
                .order_by(Metadata.key, Metadata.value)

        return set([item[0] for item in items])

    @classmethod
    def deactivate(cls, name):
        for item in Metadata.get(name):
            db.session.delete(item)

    def save(self):
        db.session.add(self)
