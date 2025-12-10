import pytest
from src.lambda_function import lambda_handler
from src.custom_exception import GenericException
from src.constants import Constants
from src.lambda_function import parse_s3_event
from src.lambda_function import log_and_notify

@pytest.fixture
def s3_event():
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "test-bucket"},
                    "object": {"key": "folder%2Ftestfile.csv"}
                }
            }
        ]
    }

@pytest.fixture
def context():
    return {}  # mock AWS context (usually not used)

def test_lambda_handler_success(monkeypatch, s3_event, context):
    def mock_data_compare(bucket, key):
        return {"result": "ok"}

    def mock_insert_log(data):
        assert data == {"result": "ok"}

    def mock_send_message(message, data):
        assert Constants.SUCCESS_MESSAGE in message

    monkeypatch.setattr("src.lambda_function.data_compare", mock_data_compare)
    monkeypatch.setattr("src.lambda_function.db_handler.insert_data_log_api", mock_insert_log)
    monkeypatch.setattr("src.lambda_function.utils.send_teams_message", mock_send_message)

    result = lambda_handler(s3_event, context)
    assert result == {"result": "ok"}


def test_lambda_handler_general_exception(monkeypatch, s3_event, context):
    def mock_data_compare(bucket, key):
        raise ValueError("Unexpected error")

    def mock_error_report(file_name, exc):
        return {"error": "Unexpected error"}

    def mock_insert_log(data):
        assert data == {"error": "Unexpected error"}

    def mock_send_message(message, data):
        assert Constants.FAILED_MESSAGE in message

    monkeypatch.setattr("src.lambda_function.data_compare", mock_data_compare)
    monkeypatch.setattr("src.lambda_function.utils.generate_error_report", mock_error_report)
    monkeypatch.setattr("src.lambda_function.db_handler.insert_data_log_api", mock_insert_log)
    monkeypatch.setattr("src.lambda_function.utils.send_teams_message", mock_send_message)

    result = lambda_handler(s3_event, context)
    assert result == {"error": "Unexpected error"}

def test_parse_s3_event(s3_event):
    file_key, bucket, file_name = parse_s3_event(s3_event)
    assert file_key == "folder/testfile.csv"
    assert bucket == "test-bucket"
    assert file_name == "testfile.csv"

def test_log_and_notify(monkeypatch):
    called = {"log": False, "teams": False}

    def mock_insert_data_log_api(data):
        called["log"] = True
        assert data == {"key": "value"}

    def mock_send_teams_message(message, data):
        called["teams"] = True
        assert message == "testfile.csv - Upload done"
        assert data == {"key": "value"}

    monkeypatch.setattr("src.lambda_function.db_handler.insert_data_log_api", mock_insert_data_log_api)
    monkeypatch.setattr("src.lambda_function.utils.send_teams_message", mock_send_teams_message)

    log_and_notify("testfile.csv", "Upload done", {"key": "value"})

    assert called["log"]
    assert called["teams"]

def test_lambda_handler_generic_exception(monkeypatch, s3_event, context):
    from src import lambda_function  # Ensure you raise from the same module

    def mock_data_compare(bucket, key):
        raise lambda_function.GenericException(400, "Bad Request")  # 👈 FIXED

    def mock_error_report(file_name, exc):
        return {"error": "Bad Request"}

    def mock_insert_log(data):
        assert data == {"error": "Bad Request"}

    def mock_send_message(message, data):
        assert Constants.FAILED_MESSAGE in message

    monkeypatch.setattr("src.lambda_function.data_compare", mock_data_compare)
    monkeypatch.setattr("src.lambda_function.utils.generate_error_report", mock_error_report)
    monkeypatch.setattr("src.lambda_function.db_handler.insert_data_log_api", mock_insert_log)
    monkeypatch.setattr("src.lambda_function.utils.send_teams_message", mock_send_message)

    result = lambda_function.lambda_handler(s3_event, context)
    assert result == {"error": "Bad Request"}
