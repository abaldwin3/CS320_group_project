import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

import pytest

from ypd.model import Base, Session, engine, project


class TestProject(TestCase):
    @pytest.fixture
    def client():
        db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True

        with flaskr.app.test_client() as client:
            with flaskr.app.app_context():
                flaskr.init_db()
            yield client

        os.close(db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(client):
        """Start with a blank database."""

        rv = client.get('/')
        assert b'No entries here so far' in rv.data

        rv = client.get('/user')
        assert b'No entries here so far' in rv.data

    def login(client, username, password):
        return client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)