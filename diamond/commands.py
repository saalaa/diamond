from .app import app
from .models import db_init, db_drop

@app.cli.command('initdb')
def initdb():
    db_init()

@app.cli.command('dropdb')
def dropdb():
    db_drop()
