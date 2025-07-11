import pytest
from types import SimpleNamespace
from src.database import Database

# Dummy/Fake classes
class FakeConnection:
    def __init__(self):
        self.closed = False

class FakePool:
    def __init__(self, minconn, maxconn, **kwargs):
        self.conn = FakeConnection()

    def getconn(self):
        return self.conn

    def putconn(self, conn):
        conn.closed = False

    def closeall(self):
        self.conn.closed = True

@pytest.fixture
def mock_constants(monkeypatch):
    fake_constants = SimpleNamespace(
        DB_SECRET_NAME="fake_secret_name",
        DB_NAME="test_db",
        USERNAME="test_user",
        HOST="localhost",
        PORT="5432"
    )
    monkeypatch.setattr("src.database.Constants", fake_constants)

@pytest.fixture
def mock_secret(monkeypatch):
    monkeypatch.setattr("src.database.get_secret_dict", lambda name: {"SecretString": "test_pass"})

@pytest.fixture
def mock_pool(monkeypatch):
    monkeypatch.setattr("src.database.pool.SimpleConnectionPool", FakePool)

def test_get_and_release_connection(mock_constants, mock_secret, mock_pool):
    db = Database()
    conn = db.get_connection()
    assert isinstance(conn, FakeConnection)
    db.release_connection(conn)
    assert conn.closed is False

def test_close_all_connections(mock_constants, mock_secret, mock_pool):
    db = Database()
    conn = db.get_connection()
    db.close_all_connections()
    assert conn.closed is True