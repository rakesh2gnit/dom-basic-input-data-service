import pytest
import pandas as pd
from datetime import datetime
from src.constants import Constants
from src.database import Database
import json
from src.db_handler import (
    run_query,
    get_column_template,
    load_drive_template,
    get_existing_file_name,
    load_drive_content,
    get_drive_table_data,
    insert_data_log_api,
    insert_drive_table_data,
    update_drive_table_data
)

# Mock run_query using monkeypatch
@pytest.fixture
def mock_run_query(monkeypatch):
    def _mock(return_value=None):
        monkeypatch.setattr("src.db_handler.run_query", lambda *args, **kwargs: return_value)
    return _mock

def test_get_column_template(mock_run_query):
    mock_run_query(("col1",))
    assert get_column_template() == ("col1",)

def test_load_drive_template(mock_run_query):
    mock_run_query(1001)
    assert load_drive_template() == 1001

def test_get_existing_file_name(mock_run_query):
    df = pd.DataFrame([{"file_name": "test_file.csv"}])
    mock_run_query(df)
    result = get_existing_file_name()
    assert isinstance(result, pd.DataFrame)
    assert result.iloc[0]["file_name"] == "test_file.csv"

def test_load_drive_content(mock_run_query):
    mock_run_query(2002)
    result = load_drive_content("test.csv", "s3://bucket/test.csv")
    assert result == 2002

def test_get_drive_table_data(mock_run_query):
    df = pd.DataFrame([{"key": "1", "val": "x"}])
    mock_run_query(df)
    result = get_drive_table_data(["key", "val"])
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["key", "val"]

def test_insert_data_log_api(mock_run_query):
    mock_run_query(None)
    data = {
        "drive_name": "test_drive",
        "file_name": "test_file.csv",
        "status": 1,
        "progress": 100,
        "error_report": "No errors",
        "environment": "test",
        "created_timestamp": datetime.now().strftime(Constants.TIMESTAMP_FORMAT)
    }
    result = insert_data_log_api(data)
    assert result is None  # Assuming run_query returns None on success

# --- Test for update_drive_table_data ---
def test_update_drive_table_data(monkeypatch):
    df_database = pd.DataFrame([
        {"key": "abc123", "col1": "old", "status": 3}
    ])

    df_to_update = pd.DataFrame([
        {"key": "abc123", "col1": "new", "status": 2, "updated": "now", "action": None, "changes": None}
    ])

    called = {"query": False}

    def fake_run_query(query, params=None, fetch=None):
        called["query"] = True
        assert "UPDATE" in query
        return None

    monkeypatch.setattr("src.db_handler.run_query", fake_run_query)

    update_drive_table_data(df_database, df_to_update, ["col1", "updated", "action", "changes"])
    assert called["query"] is True

class FakeLogger:
    def __init__(self):
        self.logs = {"info": [], "error": []}

    def info(self, msg):
        self.logs["info"].append(msg)

    def error(self, msg):
        self.logs["error"].append(msg)

@pytest.fixture
def mock_logger(monkeypatch):
    fake_logger = FakeLogger()
    monkeypatch.setattr("src.db_handler.logger", fake_logger)
    return fake_logger

def test_insert_drive_table_data(mock_run_query, mock_logger):
    df = pd.DataFrame([
        {"key": "k1", "col1": "value1", "status": 0, "action": None, "changes": None}
    ])
    mock_run_query(None)

    insert_drive_table_data(df, ["key", "col1", "status", "action", "changes"])

    assert any("Inserted row" in msg for msg in mock_logger.logs["info"])