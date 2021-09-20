""" core_test.py """

from .context import smart_canvas
import pytest

def test_hmm():
    assert smart_canvas.core.get_hmm() == 'hmmm...'
