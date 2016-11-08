from diamond.db import db

class Metadata(db.Model):
    __tablename__ = 'metadata'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, nullable=False) # ForeignKey('documents.slug')
    key = db.Column(db.String, nullable=False)
    value = db.Column(db.String, nullable=False)

    @classmethod
    def get(self, slug):
        return Metadata.query \
                .filter(Metadata.slug == slug) \
                .order_by(Metadata.key, Metadata.value) \
                .all()

    @classmethod
    def search(self, key, value):
        items = db.session.query(Metadata.slug) \
                .filter(Metadata.key == key) \
                .filter(Metadata.value == value) \
                .order_by(Metadata.key, Metadata.value)

        return set([item[0] for item in items])

    @classmethod
    def deactivate(cls, slug):
        for item in Metadata.get(slug):
            db.session.delete(item)

    def save(self):
        db.session.add(self)

db.Index('idx_metadata_slug', Metadata.slug)
db.Index('idx_metadata_key_value', Metadata.key, Metadata.key)
