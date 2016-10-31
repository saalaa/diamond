from app import app
from models import db_init, db_drop

@app.cli.command('init-db')
def init_db():
    db_init()

@app.cli.command('drop-db')
def drop_db():
    db_drop()
