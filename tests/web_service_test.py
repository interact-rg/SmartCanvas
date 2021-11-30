""" web_service_test.py """
from io import BytesIO
from tempfile import mkdtemp

import cv2
import pytest
from flask_socketio import SocketIOTestClient
import numpy as np

from web import create_app
from web.main.events import cv_to_b64, b64_to_cv

TOKEN = 'test-token-ea520c84'
FINGER_IMAGE_FOLDER_PATH = "tests/test_assets/finger_pictures"


@pytest.fixture()
def sio_client():
    '''
    https://flask-socketio.readthedocs.io/en/latest/api.html?highlight=test#flask_socketio.SocketIO.test_client
    '''
    config = {
        "DEBUG": True,
        "TESTING": True,
        "TOKENS": {
            TOKEN: "Client-1",
        },
    }
    app = create_app(config)
    sio_client = SocketIOTestClient(app, app.config["socketio"])
    yield sio_client

class TestSocketIO(object):
    RESOURCE_URL = "/"

    def test_connection(self, sio_client):
        sio_client.connect()
        connection_state = sio_client.is_connected()
        assert connection_state is True
        sio_client.disconnect()
        connection_state = sio_client.is_connected()
        assert connection_state is False

    def test_emit(self, sio_client):
        sio_client.connect()
        frame = cv2.imread(f"{FINGER_IMAGE_FOLDER_PATH}/1.jpeg")
        w, h, c = frame.shape
        answers = []
        max_tries = 5000
        while not answers and max_tries:
            sio_client.emit(
                "produce", f'data:image/jpeg;base64,{cv_to_b64(frame)}')
            answers = sio_client.get_received()
            max_tries -= 1
        first_answer = answers[0]
        first_arg = first_answer["args"][0]
        b64_frame = first_arg.split(",")[1]
        processed_frame = b64_to_cv(b64_frame)
        p_w, p_h, p_c = frame.shape
        assert w == p_w
        assert h == p_h
        assert c == p_c
        sio_client.disconnect()
        connection_state = sio_client.is_connected()
        assert connection_state is False


@pytest.fixture()
def client():
    '''
    based on http://flask.pocoo.org/docs/1.0/testing/
    '''
    config = {
        "DEBUG": True,
        "TESTING": True,
        "TOKENS": {
            TOKEN: "Client-1",
        },
    }
    app = create_app(config)
    yield app.test_client()


class TestIndex(object):
    RESOURCE_URL = "/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        assert resp.data is not None


class TestFileUpload(object):
    RESOURCE_URL = "/upload"

    def test_get(self, client):
        # Fail without token
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 405
        # Fail with token
        resp = client.get(
            self.RESOURCE_URL,
            headers={'Authorization': f'Bearer {TOKEN}'}
        )
        assert resp.status_code == 405

    def test_post(self, client):
        # Fail without token
        contents = b'test-file-contents'
        data = dict(file=(BytesIO(contents), 'test-1.jpeg'))
        resp = client.post(
            self.RESOURCE_URL,
            data=data,
            content_type='multipart/form-data'
        )
        assert resp.status_code == 401
        # Fail with wrong token
        data = dict(file=(BytesIO(contents), 'test-2.jpeg'))
        resp = client.post(
            self.RESOURCE_URL,
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer wrong-token-123'}
        )
        assert resp.status_code == 401
        # Succeed with valid token
        data = dict(file=(BytesIO(contents), 'test-3.jpeg'))
        resp = client.post(
            self.RESOURCE_URL,
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {TOKEN}'}
        )
        assert resp.status_code == 201


class TestFileDownload(object):
    RESOURCE_URL = "/uploads"
    UPLOAD_URL = "/upload"

    def test_get(self, client):
        contents = b'test-file-contents'
        # Put valid file into the system
        data = dict(file=(BytesIO(contents), 'valid-file.jpeg'))
        resp = client.post(
            self.UPLOAD_URL,
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {TOKEN}'}
        )
        picture_url = resp.data.decode("utf-8")
        picture_name = picture_url.split("/")[-1]
        # Succeed with token, valid picture
        resp = client.get(
            f'{self.RESOURCE_URL}/{picture_name}',
            follow_redirects=True,
            headers={'Authorization': f'Bearer {TOKEN}'}
        )
        assert resp.status_code == 200
        assert resp.data == contents
        # Fail without token, valid picture
        resp = client.get(
            f'{self.RESOURCE_URL}/{picture_name}',
            follow_redirects=True
        )
        assert resp.status_code == 401
        # Fail without token, invalid picture
        resp = client.get(
            f'{self.RESOURCE_URL}/not-going-to-work.jpeg',
            follow_redirects=True
        )
        assert resp.status_code == 401
        # Fail with token, invalid picture
        resp = client.get(
            f'{self.RESOURCE_URL}/not-going-to-work.jpeg',
            headers={'Authorization': f'Bearer {TOKEN}'},
            follow_redirects=True
        )
        assert resp.status_code == 404

    def test_post(self, client):
        contents = b'test-file-contents'
        # Put valid file into the system
        data = dict(file=(BytesIO(contents), 'valid-file.jpeg'))
        resp = client.post(
            self.UPLOAD_URL,
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {TOKEN}'},
        )
        picture_url = resp.data.decode("utf-8")
        picture_name = picture_url.split("/")[-1]
        # Fail with real picture, valid picture
        data = dict(file=(BytesIO(contents), picture_name))
        resp = client.post(
            resp.data,
            follow_redirects=True,
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {TOKEN}'}
        )
        assert resp.status_code == 405
        # Fail without token, invalid picture
        data = dict(file=(BytesIO(contents), 'test-1.jpeg'))
        resp = client.post(
            f'{self.RESOURCE_URL}/not-going-to-work.jpeg',
            follow_redirects=True,
            data=data,
            content_type='multipart/form-data'
        )
        assert resp.status_code == 405
        # Fail with token, invalid picture
        data = dict(file=(BytesIO(contents), 'test-2.jpeg'))
        resp = client.post(
            f'{self.RESOURCE_URL}/not-going-to-work.jpeg',
            follow_redirects=True,
            data=data,
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {TOKEN}'}
        )
        assert resp.status_code == 405
