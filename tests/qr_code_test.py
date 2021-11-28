""" qr_code_test.py """
import os
from uuid import uuid4
from tempfile import mkstemp

import pytest
import cv2

from smart_canvas.qr_code import create_qr_code


@pytest.fixture
def qr_detector():
    yield cv2.QRCodeDetector()


class TestQRCode:
    def test_create(self, qr_detector):
        url = 'www.address.com'
        cv2_image = create_qr_code(url)
        data, bbox, _ = qr_detector.detectAndDecode(cv2_image)
        assert bbox is not None
        assert data == url

    def test_short_url(self, qr_detector):
        url = f'https://www.address.com/{str(uuid4())[:3]}'
        cv2_image = create_qr_code(url)
        data, bbox, _ = qr_detector.detectAndDecode(cv2_image)
        assert bbox is not None
        assert data == url
