""" helpers_test.py """

from .context import smart_canvas
import pytest

def test_hmm():
    assert smart_canvas.helpers.get_answer() == True
