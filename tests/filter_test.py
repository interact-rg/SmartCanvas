""" filter_test.py """

import cv2
import pytest
import numpy as np
import os

from smart_canvas.filters.carousel import FilterCarousel
from smart_canvas.masker import ForegroundMask
from smart_canvas.filters.base import Filter

def build_filter_catalog():
    carousel = FilterCarousel()
    return [
        pytest.param(filter, name, id=name) for name, filter in carousel.catalog.items()
    ]

def build_frame_catalog():
    return [
        pytest.param(cv2.imread("tests/test_assets/normal_images/neutral.png"), 'neutral', id="neutral"),
        pytest.param(cv2.imread("tests/test_assets/normal_images/glasses.png"), 'glasses', id="glasses"),
        pytest.param(cv2.imread("tests/test_assets/normal_images/low_light.png"), 'low_light', id="low_light"),
        pytest.param(cv2.imread("tests/test_assets/normal_images/partially_framed.png"), 'partially_framed', id="partially_framed"),
    ]

@pytest.fixture(scope="module")
def masker():
    yield ForegroundMask()
    


@pytest.mark.parametrize("filter, name", build_filter_catalog())
class TestFilters(object):
    def test_filter_with_image(self, filter: Filter, name: str):
        frame = cv2.imread("tests/test_assets/small_image/image.png")
        mask = cv2.imread("tests/test_assets/small_image/mask.png")
        w, h, c = frame.shape
        filtered_frame = filter.filter_frame(frame, mask)
        p_w, p_h, p_c = filtered_frame.shape
        assert w == p_w, f'wrong width in: {name}'
        assert h == p_h, f'wrong height in: {name}'
        assert c == p_c, f'wrong amount of color channels in: {name}'

    def test_filter_with_black_image(self, filter: Filter, name: str):
        frame = np.zeros((50, 50, 3), np.uint8)
        mask = np.zeros((50, 50, 3), np.uint8)
        w, h, c = frame.shape
        filtered_frame = filter.filter_frame(frame, mask)
        p_w, p_h, p_c = filtered_frame.shape
        assert w == p_w, f'wrong width in: {name}'
        assert h == p_h, f'wrong height in: {name}'
        assert c == p_c, f'wrong amount of color channels in: {name}'

    def test_filter_with_white_image(self, filter: Filter, name: str):
        frame = np.zeros((50, 50, 3), np.uint8)
        mask = np.zeros((50, 50, 3), np.uint8)
        frame[:] = 255
        mask[:] = 255
        w, h, c = frame.shape
        filtered_frame = filter.filter_frame(frame, mask)
        p_w, p_h, p_c = filtered_frame.shape
        assert w == p_w, f'wrong width in: {name}'
        assert h == p_h, f'wrong height in: {name}'
        assert c == p_c, f'wrong amount of color channels in: {name}'

    # TODO: This test breaks alot of filters if smaller size image
    def test_filter_with_min_imagesize(self, filter: Filter, name: str):
        frame = (np.random.random((5, 5, 3)) * 255).astype(np.uint8) # min input size
        mask = (np.random.random((5, 5, 3)) * 255).astype(np.uint8) # min input size
        w, h, c = frame.shape
        filtered_frame = filter.filter_frame(frame, mask)
        p_w, p_h, p_c = filtered_frame.shape
        assert w == p_w, f'wrong width in: {name}'
        assert h == p_h, f'wrong height in: {name}'
        assert c == p_c, f'wrong amount of color channels in: {name}'

    def test_filter_with_max_imagesize(self, filter: Filter, name: str):
        frame = (np.random.random((720, 1280, 3)) * 255).astype(np.uint8) # max camera resolution
        mask = (np.random.random((720, 1280, 3)) * 255).astype(np.uint8) # max camera resolution
        w, h, c = frame.shape
        filtered_frame = filter.filter_frame(frame, mask)
        p_w, p_h, p_c = filtered_frame.shape
        assert w == p_w, f'wrong width in: {name}'
        assert h == p_h, f'wrong height in: {name}'
        assert c == p_c, f'wrong amount of color channels in: {name}'

    def test_return_type(self, filter: Filter, name: str):
        frame = (np.random.random((100, 100, 3)) * 255).astype(np.uint8) 
        mask = (np.random.random((100, 100, 3)) * 255).astype(np.uint8)
        filtered_frame = filter.filter_frame(frame, mask)
        assert isinstance(filtered_frame, np.ndarray), f'wrong return type in: {name}'

    @pytest.mark.parametrize("frame, frame_name", build_frame_catalog())
    def test_with_image_output(self, filter: Filter, name: str, masker: ForegroundMask, frame: np.ndarray, frame_name: str):
        mask = masker.apply(frame)
        filtered_frame = filter.filter_frame(frame, mask)
        w, h, c = frame.shape
        p_w, p_h, p_c = filtered_frame.shape
        assert w == p_w, f'wrong width in: {name}'
        assert h == p_h, f'wrong height in: {name}'
        assert c == p_c, f'wrong amount of color channels in: {name}'
        os.makedirs(f'tests/output/{name}', exist_ok=True)
        cv2.imwrite(f'tests/output/{name}/{frame_name}.png', filtered_frame)