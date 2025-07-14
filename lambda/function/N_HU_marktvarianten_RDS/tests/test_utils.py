import pytest
import pandas as pd
import json

from src.utils import (
    generate_error_report,
    get_secret_dict,
    send_teams_message,
    validate_column_template
)
from src.constants import Constants


def test_generate_error_report_with_custom_exception():
    class DummyException(Exception):
        def __init__(self):
            self.message = "Test error"

    file_name = "test.csv"
    exc = DummyException()
    result = generate_error_report(file_name, exc)

    assert result["file_name"] == file_name
    assert result["status"] == Constants.PROCESS_FAILED
    assert "Test error" in result["error_report"][0]["error_message"]
    assert "created_timestamp" in result

def test_get_secret_dict(monkeypatch):
    class DummyClient:
        def get_secret_value(self, SecretId):
            return {"SecretString": json.dumps({"webhook_url": "http://url"})}

    monkeypatch.setattr("utils.boto3.session.Session", lambda: type("Session", (), {"client": lambda self, service_name, region_name: DummyClient()})())
    monkeypatch.setattr("utils.Constants.AWS_REGION", "us-east-1")

    result = get_secret_dict("fake_secret")
    assert "SecretString" in result

def test_send_teams_message_skipped(monkeypatch):
    monkeypatch.setenv("ENV", "TEST")
    # Should not raise error
    send_teams_message("Test Message", {"drive_name": "Drive1"})

def test_validate_column_template(monkeypatch):
    df = pd.DataFrame(columns=["col1", "col2", "col3"])
    template = {"col1": {}, "col2": {}, "col3": {}}
    # Should not raise error
    validate_column_template(template, df)