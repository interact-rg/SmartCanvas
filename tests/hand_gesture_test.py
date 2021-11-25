""" hand_gesture_test.py """

import cv2
import pytest

from smart_canvas.gesture_detection import HandDetect

FINGER_IMAGE_FOLDER_PATH = "tests/test_assets/finger_pictures"


class TestFingerCounter(object):
    @pytest.mark.parametrize("test_input, expected", [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    def test_finger_image(self, test_input, expected):
        hand_detector = HandDetect()
        frame = cv2.imread(f"{FINGER_IMAGE_FOLDER_PATH}/{test_input}.jpeg")
        count = hand_detector.count_fingers(frame)
        assert count is expected
        assert count is not (expected + 1)
        assert count is not (expected - 1)
