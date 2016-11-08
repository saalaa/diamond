from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from diamond.app import app

db = SQLAlchemy(app)
migrate = Migrate(app, db)
