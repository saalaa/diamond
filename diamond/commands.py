from .app import app
from .models import setup

@app.cli.command('initdb')
def initdb():
    setup()
