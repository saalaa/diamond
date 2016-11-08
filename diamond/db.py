from flask_sqlalchemy import SQLAlchemy
from diamond.app import app

db = SQLAlchemy(app)
