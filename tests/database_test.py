from smart_canvas.database import Database
import datetime


@pytest.fixture()
def test_database_upload(monkeypatch):

    def mock_upload():
        pass


    base = Database()
    base.insert_blob(r"assets\logo.png")

@pytest.fixture()
def test_database_download(monkeypatch):
    base = Database()
    #download image with image_id = 1
    base.download(1)