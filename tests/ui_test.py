""" ui_test.py """

import pytest

from smart_canvas.ui import UI
from unittest.mock import patch



class TestUI(object):
    @pytest.fixture()
    def ui():
        yield UI('test')