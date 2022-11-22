""" hand_gesture_test.py """

import cv2
import pytest

from smart_canvas.gesture_detection import HandDetect

FINGER_IMAGE_FOLDER_PATH = "tests/test_assets/finger_pictures"


class TestFingerCounter(object):
    @pytest.mark.parametrize("test_input, expected", [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)])
    def test_finger_image(self, test_input, expected):
        hand_detector = HandDetect()
        frame = cv2.imread(f"{FINGER_IMAGE_FOLDER_PATH}/{test_input}.jpeg")
        count, gesture = hand_detector.count_fingers(frame)
        print(count)
        assert count is expected
        assert count is not (expected + 1)
        assert count is not (expected - 1)

    @pytest.mark.parametrize("test_input, expected", [("spiderman", "SPIDERMAN SIGN"), ("thumbsup", "THUMBS UP"), ("thumbsdown", "THUMBS DOWN"), ("Vsign", "V SIGN")])
    def test_gesture_image(self, test_input, expected):
        hand_detector = HandDetect()
        frame = cv2.imread(f"{FINGER_IMAGE_FOLDER_PATH}/{test_input}.jpeg")
        count, gesture = hand_detector.count_fingers(frame)
        print(gesture)
        gesture = str(gesture["LEFT"])
        assert gesture == expected