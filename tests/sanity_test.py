""" sanity_test.py """

import pytest

class TestPackageImports:
    def test_smart_canvas(self):
        try:
            import smart_canvas.core
            from smart_canvas.image_store import ImageStore
            from queue import Queue
            q_producer = Queue(maxsize=1)
            core = smart_canvas.core.CanvasCore(q_producer, ImageStore())
            core.start()
            core.stop()
            q_producer.put(None)
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
        assert True == True