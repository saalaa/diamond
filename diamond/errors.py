from flask import render_template

from .app import app

@app.errorhandler(Exception)
def handle_bad_request(e):
    return render_template('error.j2', error='default'), 500
