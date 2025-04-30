""" hand_gesture_test.py """

import cv2
import pytest

from smart_canvas.gesture_detection_using_model import GestureDetection

FINGER_IMAGE_FOLDER_PATH = "tests/test_assets/finger_pictures"


class TestFingerCounter(object):
    @pytest.mark.parametrize("test_input, expected", [("spiderman", "SPIDERMAN SIGN"), ("thumbsup", "THUMBS UP"), ("thumbsdown", "THUMBS DOWN"), ("Vsign", "V SIGN")])
    def test_gesture_image(self, test_input, expected):
        hand_detector = GestureDetection()
        frame = cv2.imread(f"{FINGER_IMAGE_FOLDER_PATH}/{test_input}.jpeg")
        result = hand_detector.detect_gestures(frame)
        print(result)
        if result:
            gesture = str(result[0])
            assert gesture == expected
        else:
            assert result is None, "No gesture detected"