# When this file exists, pytest automatically adds `diamond` to the path; this
# file is here so that the tests can import `diamond` correctly.

import pytest

from diamond.app import app
from diamond.db import db


@pytest.fixture
def client():
    with app.app_context():
        db.drop_all()
        db.create_all()

        yield app.test_client()
