from smart_canvas.database import Database
import datetime
import pytest
from unittest.mock import MagicMock
import os
import sqlite3


@pytest.fixture
def session(): # 1
    connection = sqlite3.connect(':memory:')
    db_session = connection.cursor()
    yield db_session
    connection.close()


@pytest.fixture
def setup_db(session): # 2
    session.execute('''CREATE TABLE numbers
                          (number text, existing boolean)''')
    session.execute('INSERT INTO numbers VALUES ("+3155512345", 1)')
    session.execute('Select * from "numbers"')
    session.connection.commit()

def test_get_mock():
    session = MagicMock() # 1
    executor = MagicMock()
    session.execute = executor
    cache = CacheService(session) # 2
    cache.get_status('+3155512345')
    executor.assert_called_once_with('SELECT existing FROM numbers WHERE number=?', ('+3155512345',)) # 3

def test_get(session): # 1
    print("!!!!!!!!!!!!!!!!TESTING GET METHOD!!!!!!!!!!!")
    cache = CacheService(session) # 2
    existing = cache.get_status('+3155512345') # 3
    assert existing

def test_get_unknown(session):
    session = MagicMock() # 1
    executor = MagicMock()
    session.execute = executor
    cache = CacheService(session) # 2
    assert cache.get_status('+315554444') is None

'''
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
    assert ratio == 0.5'''



@pytest.fixture
def cache(session): # 1
    return CacheService(session)

@pytest.mark.usefixtures("setup_db")
def test_get(cache): # 2
    existing = cache.get_status('+3155512345')
    assert existing

class CacheService:
    def __init__(self, session): # 1
        self.session = session # 2

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
