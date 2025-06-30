import pytest
from unittest.mock import patch, MagicMock
from src.database import Database
from custom_exception import DatabaseException

@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("dbname", "test_db")
    monkeypatch.setenv("username", "test_user")
    monkeypatch.setenv("host", "localhost")
    monkeypatch.setenv("port", "5432")

@pytest.fixture
def mock_get_secret_dict():
    with patch("src.database.get_secret_dict") as mock_secret:
        mock_secret.return_value = {"SecretString": "test_password"}
        yield mock_secret

@pytest.fixture
def mock_connection_pool():
    with patch("src.database.pool.SimpleConnectionPool") as mock_pool:
        mock_instance = MagicMock()
        mock_pool.return_value = mock_instance
        yield mock_instance

def test_database_singleton(mock_env_vars, mock_get_secret_dict, mock_connection_pool):
    db1 = Database()
    db2 = Database()
    assert db1 is db2, "Database class is not a singleton"

def test_get_connection_success(mock_env_vars, mock_get_secret_dict, mock_connection_pool):
    db = Database()
    mock_conn = MagicMock()
    mock_connection_pool.getconn.return_value = mock_conn

    conn = db.get_connection()
    assert conn == mock_conn, "Failed to get connection from pool"
    mock_connection_pool.getconn.assert_called_once()

def test_get_connection_failure(mock_env_vars, mock_get_secret_dict, mock_connection_pool):
    db = Database()
    mock_connection_pool.getconn.side_effect = Exception("Connection error")

    with pytest.raises(DatabaseException, match="Error getting connection from pool: Connection error"):
        db.get_connection()

def test_release_connection_success(mock_env_vars, mock_get_secret_dict, mock_connection_pool):
    db = Database()
    mock_conn = MagicMock()

    db.release_connection(mock_conn)
    mock_connection_pool.putconn.assert_called_once_with(mock_conn)

def test_release_connection_failure(mock_env_vars, mock_get_secret_dict, mock_connection_pool):
    db = Database()
    mock_conn = MagicMock()
    mock_connection_pool.putconn.side_effect = Exception("Release error")

    with pytest.raises(DatabaseException, match="Error releasing connection back to pool: Release error"):
        db.release_connection(mock_conn)

def test_close_all_connections_success(mock_env_vars, mock_get_secret_dict, mock_connection_pool):
    db = Database()

    db.close_all_connections()
    mock_connection_pool.closeall.assert_called_once()

def test_close_all_connections_failure(mock_env_vars, mock_get_secret_dict, mock_connection_pool):
    db = Database()
    mock_connection_pool.closeall.side_effect = Exception("Close error")

    with pytest.raises(DatabaseException, match="Error closing all connections in pool: Close error"):
        db.close_all_connections()