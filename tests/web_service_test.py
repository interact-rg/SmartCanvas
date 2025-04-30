""" web_service_test.py """
import os

import cv2
import pytest
from flask_socketio import SocketIOTestClient

from web import create_app
from web.main.imgutils import cv_to_b64, b64_to_cv
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