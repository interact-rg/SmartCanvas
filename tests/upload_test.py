""" upload_test.py """
import os

import pytest

from smart_canvas.mock_server import MockServer
from smart_canvas.upload import upload_image

TOKEN = 'test-token-ea520c84'


@pytest.fixture(scope='session')
def mock_server():
    config = {
        "DEBUG": True,
        "TESTING": True,
        "TOKENS": {TOKEN: "Client-1"},
    }
    server = MockServer(config, port=5050)
    server.start()
    yield server
    server.stop()

@pytest.mark.skip(reason="upload functionality not supported by current webapp implementation")
def test_upload(mock_server):
    # Succeed with valid token
    url = upload_image(
        image_path='assets/logo.png',
        url=mock_server.url,
        auth_token=TOKEN,
    )
    assert url != ''
    # Fail with invalid token
    url = upload_image(
        image_path='assets/logo.png',
        url=mock_server.url,
        auth_token='not-going-to-work',
    )
    assert 'Unauthorized Access' in url
