from flask import render_template

from app import app

if not app.config['FLASK_DEBUG']:
    @app.errorhandler(Exception)
    def default_error_handler(e):
        return render_template('error.j2', error='An error has occured; '
                'please contact the administrator or try again later.'), 500
