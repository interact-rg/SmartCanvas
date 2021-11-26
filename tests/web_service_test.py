""" web_service_test.py """

import json
import os
from io import BytesIO
from tempfile import mkdtemp

import pytest

from web import create_app


@pytest.fixture
def client():
    '''
    based on http://flask.pocoo.org/docs/1.0/testing/
    '''
    os.environ['CLIENT_TOKEN'] = 'test-token-ea520c84'
    app = create_app()
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
            headers={'Authorization': f'Bearer {os.getenv("CLIENT_TOKEN")}'}
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
            headers={'Authorization': f'Bearer {os.getenv("CLIENT_TOKEN")}'}
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
            headers={'Authorization': f'Bearer {os.getenv("CLIENT_TOKEN")}'}
        )
        picture_url = resp.data.decode("utf-8")
        picture_name = picture_url.split("/")[-1]
        # Succeed with token, valid picture
        resp = client.get(
            f'{self.RESOURCE_URL}/{picture_name}',
            follow_redirects=True,
            headers={'Authorization': f'Bearer {os.getenv("CLIENT_TOKEN")}'}
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
            headers={'Authorization': f'Bearer {os.getenv("CLIENT_TOKEN")}'},
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
            headers={'Authorization': f'Bearer {os.getenv("CLIENT_TOKEN")}'},
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
            headers={'Authorization': f'Bearer {os.getenv("CLIENT_TOKEN")}'}
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
            headers={'Authorization': f'Bearer {os.getenv("CLIENT_TOKEN")}'}
        )
        assert resp.status_code == 405
