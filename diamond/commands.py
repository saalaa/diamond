from diamond.app import app
from diamond.db import db

@app.cli.command('init-db')
def init_db():
    db.create_all()

@app.cli.command('drop-db')
def drop_db():
    db.drop_all()
