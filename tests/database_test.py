from smart_canvas.database import Database
import datetime
import pytest
import mysql.connector
from unittest.mock import MagicMock


class CacheService:
    def __init__(self, session):
        self.session = session

    def get_status(self, number):
        self.session.execute('SELECT existing FROM numbers WHERE number=?', (number,))
        return self.session.fetchone()

    def save_status(self, number, existing):
        self.session.execute('INSERT INTO numbers VALUES (?, ?)', (number, existing))
        self.session.connection.commit()

    def generate_report(self):
        self.session.execute('SELECT COUNT(*) FROM numbers')
        count = self.session.fetchone()
        self.session.execute('SELECT COUNT(*) FROM numbers WHERE existing=1')
        count_existing = self.session.fetchone()
        return count_existing[0]/count[0]


    @pytest.fixture
    def session():
        connection = mysql.connector.connect(':memory:')
        db_session = connection.cursor()
        yield db_session
        connection.close()


    @pytest.fixture
    def setup_db(session):
        session.execute('''CREATE TABLE numbers
                            (number text, existing boolean)''')
        session.execute('INSERT INTO numbers VALUES ("+3155512345", 1)')
        session.connection.commit()

    def test_get_mock():
        session = MagicMock()
        executor = MagicMock()
        session.execute = executor
        cache = CacheService(session)
        cache.get_status('+3155512345')
        executor.assert_called_once_with('SELECT existing FROM numbers WHERE number=?', ('+3155512345',)) # 3




    @pytest.fixture
    def cache(session): 
        return CacheService(session)

    @pytest.mark.usefixtures("setup_db")
    def test_get(cache):
        existing = cache.get_status('+3155512345')
        assert existing

    def test_get_unknown(session):
        cache = CacheService(session)
        assert cache.get_status('+315554444') is None

    def test_save(session):
        number = '+3155512346'
        cache = CacheService(session)
        cache.save_status(number, True)
        existing = cache.get_status(number)
        assert existing

    def test_report(session):
        cache = CacheService(session)
        cache.save_status('+3155512346', True)
        cache.save_status('+3155512347', False)
        cache.save_status('+3155512348', False)
        ratio = cache.generate_report()
        assert ratio == 0.5