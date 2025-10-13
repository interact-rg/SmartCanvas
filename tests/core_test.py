""" core_test.py """

import pytest
from smart_canvas.core import CanvasCore, Painting, Idle, Startup, Active
from smart_canvas.image_store import ImageStore
from queue import Queue
import cv2
import time
import os

script_dir = os.path.dirname(__file__)
rel_path_finger = r"test_assets/finger_pictures"
rel_path_normal = r"test_assets/normal_images"
abs_file_path_finger = os.path.join(script_dir, rel_path_finger)
abs_file_path_normal = os.path.join(script_dir, rel_path_normal)


two_fingers = cv2.resize(cv2.imread(f"{abs_file_path_finger}/2.jpeg"), (1280,720), interpolation = cv2.INTER_AREA)
five_fingers = cv2.resize(cv2.imread(f"{abs_file_path_finger}/5.jpeg"), (1280, 720), interpolation = cv2.INTER_AREA)
thumbs_down = cv2.resize(cv2.imread(f"{abs_file_path_finger}/thumbs_down_720.jpg"), (1280, 720), interpolation = cv2.INTER_AREA)
face_neutral = cv2.resize(cv2.imread(f"{abs_file_path_normal}/neutral.png"), (1280, 720), interpolation = cv2.INTER_AREA)
face_neutral_with_five_fingers = cv2.resize(cv2.imread(f"{abs_file_path_normal}/neutral_with_five_fingers.png"), (1280, 720), interpolation = cv2.INTER_AREA)

@pytest.fixture()
def queue():
    yield Queue()

@pytest.fixture()
def core(queue):
    core = CanvasCore(queue, ImageStore())
    core.start()
    yield core
    core.stop()
    queue.put(None)


class TestCoreState:
    def test_smart_canvas(self, core, queue):
        assert two_fingers is not None
        assert face_neutral is not None
        assert type(core._state) is type(Startup())
        queue.put(two_fingers)
        time.sleep(0.1)
        assert type(core._state) is type(Idle())

        for _ in range(0,30):
            print(f"face")
            queue.put(face_neutral)
            time.sleep(0.1)
        assert type(core._state) is type(Active())
        
        for _ in range(0,20):
            print(f"five fingers")
            queue.put(five_fingers)
            time.sleep(0.1)

        timeout = 0
        while type(core._state) is not type(Painting()) and timeout < 100:
            print(f"not painting")
            queue.put(face_neutral_with_five_fingers)
            timeout += 1
            time.sleep(0.1)
        assert type(core._state) is type(Painting())


