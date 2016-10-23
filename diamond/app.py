from flask import Flask

from .utils import env, secret

app = Flask(__name__)

app.config.update({
    'FLASK_DEBUG': env('FLASK_DEBUG', False, bool),
    'PREVENT_INITDB': env('PREVENT_INITDB', False, bool),
    'PORT': env('PORT', 5000, int),
    'HOST': env('HOST', '0.0.0.0'),
    'DATABASE_URL': env('DATABASE_URL', 'sqlite:///diamond.db'),
    'SECRET_KEY': env('SECRET_KEY', secret()),
    'FRONTPAGE': env('FRONTPAGE', 'FrontPage')
})
