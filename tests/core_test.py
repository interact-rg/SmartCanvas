""" core_test.py """

from time import sleep
import pytest
from smart_canvas.core import CanvasCore, Filter, Idle, ShowPic, Startup
from queue import Queue
import cv2
import time

FINGER_IMAGE_FOLDER_PATH = r"tests\test_assets\finger_pictures"

two_fingers = cv2.resize(cv2.imread(f"{FINGER_IMAGE_FOLDER_PATH}/2.jpeg"), (1280,720), interpolation = cv2.INTER_AREA)
five_fingers = cv2.resize(cv2.imread(f"{FINGER_IMAGE_FOLDER_PATH}/5.jpeg"), (1280, 720), interpolation = cv2.INTER_AREA)

@pytest.fixture()
def queue():
    yield Queue()

@pytest.fixture()
def core(queue):
    core = CanvasCore(queue, screensize=(1280,720))
    core.start()
    yield core
    core.stop()
    queue.put(None)


class TestCoreState:
    def test_smart_canvas(self, core, queue):

        assert type(core._state) is type(Startup())
        queue.put(two_fingers)
        time.sleep(0.1)
        assert type(core._state) is type(Idle())
        for _ in range(0,20):
            queue.put(five_fingers)
            time.sleep(0.1)
        assert type(core._state) is type(Filter())
        queue.put(two_fingers)
        while type(core._state) is type(Filter()):
            queue.put(two_fingers)
            time.sleep(0.1)
        assert type(core._state) is type(ShowPic())


