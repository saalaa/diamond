from diamond.app import app
from diamond.db import db

@app.cli.command('init-db')
def init_db():
    '''Create all database entities.'''
    db.create_all()

@app.cli.command('drop-db')
def drop_db():
    '''Destroy all database entities (and data).'''
    db.drop_all()
