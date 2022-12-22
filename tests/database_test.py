from smart_canvas.database import Database
import datetime
import pytest
from unittest.mock import MagicMock
import os
import sqlite3


@pytest.fixture
def session():  # 1
    connection = sqlite3.connect(":memory:")
    db_session = connection.cursor()
    yield db_session
    connection.close()


@pytest.fixture
def setup_db(session):  # 2
    session.execute(
        """CREATE TABLE images (
    image_id int,
    image mediumblob,
    date_added date
    );"""
    )
    image_id = 1
    date_added = datetime.datetime.now()

    script_dir = os.path.dirname(__file__)
    rel_path = r"test_assets/finger_pictures"
    image = os.path.join(script_dir, rel_path)

    sqlite_insert_blob_query = """ INSERT INTO images
                                  (image_id, image, date_added) VALUES (?, ?, ?)"""

    image = r"test_assets/finger_pictures"
    # Convert data into tuple format
    data_tuple = (image_id, image, date_added)
    session.execute(sqlite_insert_blob_query, data_tuple)

    session.connection.commit()


@pytest.mark.usefixtures("setup_db")
def test_get_mock():
    session = MagicMock()  # 1
    executor = MagicMock()
    session.execute = executor
    cache = CacheService(session)  # 2
    cache.get_status("1")
    executor.assert_called_once_with(
        "SELECT image_id FROM images WHERE image_id=?", ("1",)
    )  # 3


@pytest.mark.usefixtures("setup_db")
def test_get(session):  # 1
    cache = CacheService(session)  # 2
    existing = cache.get_status("1")  # 3
    assert existing


@pytest.mark.usefixtures("setup_db")
def test_get_unknown(session):
    cache = CacheService(session)
    assert cache.get_status("15") is None


@pytest.mark.usefixtures("setup_db")
def test_save(session):
    number = "2"
    cache = CacheService(session)
    cache.save_status(number)
    existing = cache.get_status(number)
    assert existing


@pytest.mark.usefixtures("setup_db")
def test_delete(session):
    number = "2"
    cache = CacheService(session)
    cache.delete_item(number)
    id = cache.get_status(number)
    assert id is None


@pytest.fixture
def cache(session):  # 1
    return CacheService(session)


@pytest.mark.usefixtures("setup_db")
def test_get(cache):  # 2
    id = cache.get_status("1")
    assert id


class CacheService:
    def __init__(self, session):  # 1
        self.session = session  # 2

    def get_status(self, number):
        self.session.execute("SELECT image_id FROM images WHERE image_id=?", (number,))
        return self.session.fetchone()

    def save_status(self, number):
        image_id = number
        date_added = datetime.datetime.now()

        script_dir = os.path.dirname(__file__)
        rel_path = r"test_assets/finger_pictures/1.jpeg"
        image = os.path.join(script_dir, rel_path)
        image_to_insert = self.convert_image_to_binary(image)

        sqlite_insert_blob_query = """ INSERT INTO images
                                  (image_id, image, date_added) VALUES (?, ?, ?)"""

        image = r"test_assets/finger_pictures"
        # Convert data into tuple format
        data_tuple = (image_id, image_to_insert, date_added)
        self.session.execute(sqlite_insert_blob_query, data_tuple)
        self.session.connection.commit()

    def delete_item(self, number):
        image_id = number

        script_dir = os.path.dirname(__file__)
        rel_path = r"test_assets/finger_pictures"
        image = os.path.join(script_dir, rel_path)

        sqlite_delete_query = """DELETE FROM images WHERE image_id=?"""

        # Convert data into tuple format
        self.session.execute(sqlite_delete_query, (image_id,))

        self.session.connection.commit()

    def convert_image_to_binary(self, filename) -> bytes:
        # Convert digital data to binary format
        with open(filename, "rb") as file:
            binaryData = file.read()
        return binaryData
