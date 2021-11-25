""" sanity_test.py """

import pytest

class TestPackageImports:
    def test_smart_canvas(self):
        from smart_canvas.core import CanvasCore
        from queue import Queue
        q_producer = Queue(maxsize=1)
        core = CanvasCore(q_producer)
        core.start()
        core.stop()
        q_producer.put(None)
        assert True == True
    
    def test_web(self):
        from web import create_app
        assert True == True
