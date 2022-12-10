""" mockserver_test.py """
import time
import os

import requests
import pytest

from smart_canvas.mock_server import MockServer

TOKEN = 'test-token-ea520c84'


@pytest.fixture(scope='session')
def session():
    yield requests.Session()

@pytest.mark.skip(reason="mock_server.py not currently used for anything")
class TestMockServer(object):
    def test_config_with_token(self, session):
        config = {
            "DEBUG": True,
            "TESTING": True,
            "TOKENS": {TOKEN: "Client-1"},
        }
        server = MockServer(config, port=5050)
        server.start()
        resp = session.get(
            url=server.url
        )
        assert resp.status_code == 200
        assert resp.text != ''
        server.stop()
