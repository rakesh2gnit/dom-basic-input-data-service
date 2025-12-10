import pytest
import json
import pandas as pd
import numpy as np
from src.lambda_function import (
    lambda_handler,
    get_n_hu_marketvarianten,
    get_total_records,
    fetch_filtered_records,
    build_response
)

# -----------------------------
# Test: lambda_handler (valid)
# -----------------------------
def test_lambda_handler_valid(monkeypatch):
    event = {
        'headers': {'origin': 'https://valid.com'},
        'queryStringParameters': {'page': '1', 'pageSize': '10', 'model': 'X'}
    }

    monkeypatch.setenv("ALLOWED_ORIGINS", "https://valid.com,https://other.com")

    def mock_get_data(filters):
        return 1, 1, False, [{"model": "X"}], "2025-07-20"

    class DummyEncoder(json.JSONEncoder):
        def default(self, obj): return str(obj)

    monkeypatch.setattr("src.lambda_function.get_n_hu_marketvarianten", mock_get_data)
    monkeypatch.setattr("src.lambda_function.utils.DecimalEncoder", DummyEncoder)

    result = lambda_handler(event, None)
    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["total_records"] == 1
    assert isinstance(body["data"], list)
    assert result["headers"]["Access-Control-Allow-Origin"] == "https://valid.com"

# ---------------------------------------
# Test: get_n_hu_marketvarianten (basic)
# ---------------------------------------
def test_get_n_hu_marketvarianten(monkeypatch):
    filters = {'page': '1', 'pageSize': '2', 'model': 'X'}

    monkeypatch.setattr("src.lambda_function.get_total_records", lambda q, p: 1)

    rows = [("X", "2025-07-20T10:00:00")]
    columns = ["model", "updated"]
    monkeypatch.setattr("src.lambda_function.fetch_filtered_records", lambda q, p: (rows, columns))

    result = get_n_hu_marketvarianten(filters)

    assert result[0] == 1  # total_records
    assert result[1] == 1  # total_pages
    assert result[2] is False
    assert isinstance(result[3], list)
    assert result[4] == "2025-07-20T10:00:00"

# ----------------------------
# Test: get_total_records
# ----------------------------
def test_get_total_records(monkeypatch):
    class FakeCursor:
        def execute(self, q, p): self.data = [(42,)]
        def fetchone(self): return self.data[0]
        def __enter__(self): return self
        def __exit__(self, *args): pass

    class FakeConn:
        def cursor(self): return FakeCursor()
        def __enter__(self): return self
        def __exit__(self, *args): pass

    class FakeDB:
        def connection(self): return FakeConn()
        def release_connection(self, conn): pass

    monkeypatch.setattr("src.lambda_function.Database", lambda: FakeDB())

    count = get_total_records("FROM schema.table", [])
    assert count == 42

# ----------------------------
# Test: fetch_filtered_records
# ----------------------------
def test_fetch_filtered_records(monkeypatch):
    rows = [(1, "A")]

    class FakeCursor:
        def execute(self, q, p): pass
        def fetchall(self): return rows
        @property
        def description(self): return [("id",), ("name",)]
        def __enter__(self): return self
        def __exit__(self, *args): pass

    class FakeConn:
        def cursor(self): return FakeCursor()
        def __enter__(self): return self
        def __exit__(self, *args): pass

    class FakeDB:
        def connection(self): return FakeConn()
        def release_connection(self, conn): pass

    monkeypatch.setattr("src.lambda_function.Database", lambda: FakeDB())

    result_rows, result_cols = fetch_filtered_records("SELECT *", [])
    assert result_rows == rows
    assert result_cols == ["id", "name"]

# ----------------------------
# Test: build_response
# ----------------------------
def test_build_response_basic():
    response = build_response(200, {"message": "ok"}, "https://origin.com")
    assert response["statusCode"] == 200
    assert "Access-Control-Allow-Origin" in response["headers"]
    assert json.loads(response["body"])["message"] == "ok"
