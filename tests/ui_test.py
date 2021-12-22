""" ui_test.py """

import pytest

from smart_canvas.ui import UI
import moderngl


@pytest.fixture()
def ui():
    yield UI()


@pytest.fixture()
def ctx():
    yield moderngl.create_context(standalone=True, backend='egl')

class TestUI(object):
    
    def test_ui_mock(self, ui):
        """Do nothing"""
        ui.create_text("text_test", (0,0), 0.0)
        ui.create_progressbar("progress_test")
        ui.set_text("text_test", "testi")
        ui.show("text_test", "progress_test")
        ui.hide("text_test", "progress_test")
        ui.draw()
        assert True == True

    def test_ui_context(self, ui, ctx):
        text_name = "text_test"
        prog_name = "progress_test"
        ui.create_text(text_name, (0,0), 0.0)
        ui.create_progressbar(prog_name)
        ui.set_text(text_name, text_name)
        ui.show(text_name, prog_name)
        ui.hide(text_name, prog_name)
        ui.draw()
        assert text_name in ui.elements
        assert prog_name in ui.elements
        assert text_name in ui.texts
        # Wrong key
        with pytest.raises(KeyError):
            ui.set_text("test","test")
            ui.show("test")
            ui.hide("test")