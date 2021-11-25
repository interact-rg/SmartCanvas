""" web_service_test.py """

import json

import pytest

from web import create_app


@pytest.fixture
def client():
    '''
    based on http://flask.pocoo.org/docs/1.0/testing/
    '''
    app = create_app()
    yield app.test_client()


class TestIndex(object):
    RESOURCE_URL = "/"
    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        assert resp.data is not None
