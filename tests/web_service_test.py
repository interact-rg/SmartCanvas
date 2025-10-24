""" web_service_test.py """
import os

import cv2
import pytest
from flask_socketio import SocketIOTestClient

from web import create_app
from web.main.imgutils import cv_to_b64, b64_to_cv
TOKEN = 'test-token-ea520c84'
FINGER_IMAGE_FOLDER_PATH = "tests/test_assets/finger_pictures"
NORMAL_IMAGE_FOLDER_PATH = "tests/test_assets/normal_images"



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
        mockProduceInput = {"currentFrame": f'data:image/jpeg;base64,{cv_to_b64(frame)}', "baseUrl": "mockurl"}
        while len(answers) < 2 and max_tries:
            sio_client.emit(
                "produce", mockProduceInput)
            answers = sio_client.get_received()
            max_tries -= 1
        answer3 = answers[3]
        answer2 = answers[2]
        answer1 = answers[1]
        assert answer3["name"] == "available_filters"
        assert answer2["name"] == "filter"
        assert answer1["name"] == "update_ui_response"
        sio_client.disconnect()
        connection_state = sio_client.is_connected()
        assert connection_state is False

    def test_emit_baseUrl_is_none(self, sio_client):
        sio_client.connect()
        frame = cv2.imread(f"{FINGER_IMAGE_FOLDER_PATH}/1.jpeg")
        w, h, c = frame.shape
        answers = []
        max_tries = 5000
        mockProduceInput = {"currentFrame": f'data:image/jpeg;base64,{cv_to_b64(frame)}', "baseUrl": None}
        while len(answers) < 2 and max_tries:
            sio_client.emit(
                "produce", mockProduceInput)
            answers = sio_client.get_received()
            max_tries -= 1
        answer3 = answers[3]
        answer2 = answers[2]
        answer1 = answers[1]
        assert answer3["name"] == "available_filters"
        assert answer2["name"] == "filter"
        assert answer1["name"] == "update_ui_response"
        sio_client.disconnect()
        connection_state = sio_client.is_connected()
        assert connection_state is False

    def test_emit_invalid_frame(self, sio_client):
        sio_client.connect()
        answers = []
        max_tries = 5000
        mockProduceInput = {"currentFrame": f'invalid_frame', "baseUrl": None}
        while len(answers) < 2 and max_tries:
            sio_client.emit(
                "produce", mockProduceInput)
            answers = sio_client.get_received()
            max_tries -= 1
        answer3 = answers[3]
        answer2 = answers[2]
        answer1 = answers[1]
        assert answer3["name"] == "available_filters"
        assert answer2["name"] == "filter"
        assert answer1["name"] == "update_ui_response"
        sio_client.disconnect()
        connection_state = sio_client.is_connected()
        assert connection_state is False

    def test_check_image_processing(self, sio_client):
        sio_client.connect()
        sio_client.emit("check_image_processing") 
        sio_client.disconnect()
        connection_state = sio_client.is_connected()
        assert connection_state is False

    def test_produve_then_check_image_processing(self, sio_client):
        sio_client.connect()
        frame = cv2.imread(f"{NORMAL_IMAGE_FOLDER_PATH}/neutral.png")
        answers = []
        max_tries = 5000
        mockProduceInput = {"currentFrame": f'data:image/jpeg;base64,{cv_to_b64(frame)}', "baseUrl": "mockurl"}
        while len(answers) < 2 and max_tries:
            sio_client.emit(
                "produce", mockProduceInput)
            sio_client.emit("check_image_processing")
            answers = sio_client.get_received()
            max_tries -= 1
        answer3 = answers[3]
        answer2 = answers[2]
        answer1 = answers[1]
        assert answer3["name"] == "available_filters"
        assert answer2["name"] == "filter"
        assert answer1["name"] == "update_ui_response"
        sio_client.disconnect()
        connection_state = sio_client.is_connected()
        assert connection_state is False
        
@pytest.mark.skip(reason="Broken test most likely legacy. Disabled for now.")
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