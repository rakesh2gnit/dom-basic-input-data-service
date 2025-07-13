import pytest
from types import SimpleNamespace
from src.database import Database
from src.database import DatabaseException

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

@pytest.fixture(autouse=True)
def reset_singleton():
    Database._instance = None
    Database._connection_pool = None

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

def test_connection_context_manager(mock_constants, mock_secret, mock_pool):
    db = Database()
    with db.connection() as conn:
        assert isinstance(conn, FakeConnection)

def test_release_none_connection(mock_constants, mock_secret, mock_pool):
    db = Database()
    # Should not raise error even if connection is None
    db.release_connection(None)

def test_get_connection_raises_exception(mock_constants, mock_secret, monkeypatch):
    class BrokenPool:
        def getconn(self):
            raise Exception("Pool broken")

    monkeypatch.setattr("src.database.pool.SimpleConnectionPool", lambda *args, **kwargs: BrokenPool())
    
    db = Database()

    with pytest.raises(DatabaseException) as exc:
        db.get_connection()
    assert "Error getting connection from pool" in str(exc.value)