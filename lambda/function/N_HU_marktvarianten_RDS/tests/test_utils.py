import pytest
import pandas as pd
import json
from src import utils

from src.utils import (
    generate_error_report,
    get_secret_dict,
    send_teams_message,
    validate_column_template
)
from src.constants import Constants
from botocore.exceptions import ClientError
from src.custom_exception import AWSSecretException, ColumnValidationException


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

def test_get_secret_dict_client_error(monkeypatch):
    from src import utils

    class DummyClient:
        def get_secret_value(self, SecretId):
            raise ClientError({"Error": {"Code": "DecryptionFailure"}}, "GetSecretValue")

    monkeypatch.setattr("utils.boto3.session.Session", lambda: type("Session", (), {"client": lambda self, service_name, region_name: DummyClient()})())
    monkeypatch.setattr("utils.Constants.AWS_REGION", "us-east-1")

    with pytest.raises(utils.AWSSecretException) as exc_info:
        utils.get_secret_dict("invalid_secret")

    assert "Error retrieving secret invalid_secret" in str(exc_info.value)

def test_send_teams_message_skipped(monkeypatch):
    monkeypatch.setenv("ENV", "TEST")
    # Should not raise error
    send_teams_message("Test Message", {"drive_name": "Drive1"})

def test_validate_column_template(monkeypatch):
    df = pd.DataFrame(columns=["col1", "col2", "col3"])
    template = {"col1": {}, "col2": {}, "col3": {}}
    # Should not raise error
    validate_column_template(template, df)

def test_validate_column_template_missing_and_extra():
    df = pd.DataFrame(columns=["col1", "colX", "col3"])  # col2 is missing, colX is extra
    template = {"col1": {}, "col2": {}, "col3": {}}

    with pytest.raises(utils.ColumnValidationException) as exc_info:
        utils.validate_column_template(template, df)

    error_message = str(exc_info.value)
    assert "Missing columns: ['col2']" in error_message
    assert "Extra columns: ['colX']" in error_message
    assert "Please upload the correct sheet again." in error_message

def test_validate_column_template_raises_general(monkeypatch):
    # Trigger generic error (e.g., df has no columns attr)
    with pytest.raises(Exception):
        validate_column_template({"col1": {}}, None)

def test_send_teams_message_success(monkeypatch):
    dummy_webhook_payload = {
        "webhook_url": "http://example.com/webhook",
        "webhook_message": json.dumps({
            "@context": "",
            "sections": [{"activityTitle": "", "activitySubTitle": "", "facts": [{"value": ""}, {"value": ""}, {"value": ""}, {"value": ""}]}]
        }),
        "context_url": "http://context"
    }

    class DummyClient:
        def get_secret_value(self, SecretId):
            return {"SecretString": json.dumps(dummy_webhook_payload)}

    class DummyResponse:
        status_code = 200
        text = "OK"

    monkeypatch.setenv("ENV", "PROD")  # force run
    monkeypatch.setattr("src.utils.boto3.session.Session", lambda: type("Session", (), {"client": lambda self, svc, region_name: DummyClient()})())
    monkeypatch.setattr("src.utils.requests.post", lambda url, headers, data: DummyResponse())

    send_teams_message("Process completed", {
        "drive_name": "TestDrive",
        "progress": "100%",
        "status": "DONE",
        "environment": "DEV",
        "error_report": []
    })