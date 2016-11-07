from flask import Flask

from utils import env, secret

app = Flask(__name__)

app.config.update({
    'SQL_DEBUG': env('SQL_DEBUG', False, bool),
    'FLASK_DEBUG': env('FLASK_DEBUG', False, bool),
    'HOST': env('HOST', '0.0.0.0'),
    'PORT': env('PORT', 5000, int),
    'SQLALCHEMY_DATABASE_URI': env('DATABASE_URL', 'sqlite:///../diamond.db'),
    'SECRET_KEY': env('SECRET_KEY', secret())
})

# Fix legacy default
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
