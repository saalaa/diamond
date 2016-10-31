from app import app

from auth import *
from routes import *
from filters import *
from commands import *
from errors import *

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
