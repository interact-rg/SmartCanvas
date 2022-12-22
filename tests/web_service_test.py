""" web_service_test.py """
import os
from io import BytesIO
from tempfile import mkdtemp

import cv2
import pytest
from flask_socketio import SocketIOTestClient
import numpy as np
import shutil
from PIL import Image as im
import smart_canvas.database as db

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
        while len(answers) < 2 and max_tries:
            sio_client.emit(
                "produce", f'data:image/jpeg;base64,{cv_to_b64(frame)}')
            answers = sio_client.get_received()
            max_tries -= 1
        first_answer = answers[1]
        first_arg = first_answer["args"][0]
        b64_frame = first_arg.split(",")[1]
        processed_frame = b64_to_cv(b64_frame)
        p_w, p_h, p_c = processed_frame.shape
        assert w == p_w
        assert h == p_h
        assert c == p_c
        sio_client.disconnect()
        connection_state = sio_client.is_connected()
        assert connection_state is False

class TestWebappSWTest(object):
    def test_workflow(self, sio_client, capsys):
        sio_client.connect()
        connection_state = sio_client.is_connected()
        assert connection_state is True
        
        # Wait for idle state
        input_img = cv2.imread(f"{FINGER_IMAGE_FOLDER_PATH}/dummy.jpg")
        responses = []
        max_tries = 5000
        while len(responses) < 2 and max_tries:
            sio_client.emit(
                "produce", f'data:image/jpg;base64,{cv_to_b64(input_img)}')
            responses = sio_client.get_received()
            max_tries -= 1
        assert max_tries
        assert "current_state" == responses[0]["name"] and "Idle" in responses[0]["args"][0]

        # Show 5 fingers to start
        input_img = cv2.imread(f"{FINGER_IMAGE_FOLDER_PATH}/5_720.jpg")
        max_tries = 5000
        while max_tries:
            responses = []
            sio_client.emit(
                "produce", f'data:image/jpg;base64,{cv_to_b64(input_img)}')
            responses = sio_client.get_received()
            if "GPDR_consent" in responses[0]["args"][0]:
                break
            max_tries -= 1
        assert max_tries

        # Accept GDPR
        input_img = cv2.imread(f"{FINGER_IMAGE_FOLDER_PATH}/thumbs_up_720.jpg")
        max_tries = 5000
        while max_tries:
            responses = []
            sio_client.emit(
                "produce", f'data:image/jpg;base64,{cv_to_b64(input_img)}')
            responses = sio_client.get_received()
            if "Active" in responses[0]["args"][0]:
                break
            max_tries -= 1
        assert max_tries

        # Take picture and make sure "final" state is filter
        input_img = cv2.imread(f"{FINGER_IMAGE_FOLDER_PATH}/5_720.jpg")
        max_tries = 5000
        while max_tries:
            responses = []
            sio_client.emit(
                "produce", f'data:image/jpg;base64,{cv_to_b64(input_img)}')
            responses = sio_client.get_received()
            try:
                if "Filter" in responses[0]["args"][0]:
                    break
            except IndexError:
                pass
            max_tries -= 1
        assert max_tries

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


class TestPages(object):
    MAIN_URL = "/"
    FULLSCREEN = "/fullscreen"

    def test_get_main(self, client):
        resp = client.get(self.MAIN_URL)
        assert resp.status_code == 200
        with open(os.getcwd() + "/web/templates/index.html", "r") as f:
            response = resp.data.decode().split("\n")
            template = f.read().strip("\r").split("\n")
            diffs = 0
            for i in range(len(response)):
                if response[i] != template[i]:
                    diffs += 1
            assert diffs <= 2 #lines with 'url_for(x)' will differ
    
    def test_get_fullscreen(self, client):
        resp = client.get(self.FULLSCREEN)
        assert resp.status_code == 200
        with open(os.getcwd() + "/web/templates/fullscreen.html", "r") as f:
            response = resp.data.decode().split("\n")
            template = f.read().strip("\r").split("\n")
            diffs = 0
            for i in range(len(response)):
                if response[i] != template[i]:
                    diffs += 1
            assert diffs <= 2 #lines with 'url_for(x)' will differ



class TestFileDownload(object):
    URL_ID_1 = "/dl_image/1"
    URL_ID_2 = "/dl_image/2"
    
    def test_dl_too_old(self, client):
        if "database.db" in os.listdir():
            os.remove("database.db")
        shutil.copyfile("tests/test_assets/database/database.db", "database.db")
        
        resp = client.get(self.URL_ID_1)
        assert resp.status_code == 200
        response = resp.data.decode()
        assert "Download failed, please try again later" in response and "Requested image too old" in response
        

    def test_dl_nonexistent_id(self, client):
        if "database.db" in os.listdir():
            os.remove("database.db")
        shutil.copyfile("tests/test_assets/database/database.db", "database.db")

        resp = client.get(self.URL_ID_2)
        assert resp.status_code == 200
        response = resp.data.decode()
        assert "Download failed, please try again later" in response and "Requested image id does not exist" in response
        

    def test_dl_new(self, client):
        if "database.db" in os.listdir():
            os.remove("database.db")
        shutil.copyfile("tests/test_assets/database/database.db", "database.db")

        db_obj = db.Database()
        dummy_img = np.asarray(im.open("tests/test_assets/finger_pictures/dummy.jpg"))
        db_obj.insert_blob(dummy_img)
        resp = client.get(self.URL_ID_2)
        assert resp.status_code == 200
        with open("tests/test_assets/database/dl_reference.png", "rb") as f:
            ref = f.read()
        assert ref == resp.data


class TestAPSchedulerAPI(object):
    RESOURCE_URL = "/scheduler"

    def test_scheduler_info(self, client):
        # Fail without token
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        # Fail with token
        resp = client.get(
            self.RESOURCE_URL,
            headers={'Authorization': f'Bearer {TOKEN}'}
        )
        assert resp.status_code == 404
