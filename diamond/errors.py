import sqlalchemy

from flask import render_template

from .app import app

@app.errorhandler(sqlalchemy.exc.OperationalError)
def handle_bad_request(e):
    return render_template('error.j2', error='database'), 500
