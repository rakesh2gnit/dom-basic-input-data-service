import pytest
from src.constants import Constants
import os

def test_drive_name():
    assert Constants.DRIVE_NAME == "N_HU_Marktvarianten"

def test_environment():
    assert Constants.ENVIRONMENT == os.environ.get("ENVIRONMENT"), "ENVIRONMENT should not be None"

def test_db_schema_name():
    assert Constants.DB_SCHEMA_NAME == os.environ.get("DB_SCHEMA_NAME"), "DB_SCHEMA_NAME should not be None"

def test_column_template():
    expected_columns = {
        "BR": "br",
        "AA": "aa",
        "AJ/MOPF": "aj_mopf",
        "AJ/MOPF-Paket": "aj_paket",
        "Paaket PU-Termin": "paket_pu_termin",
        "Paketname": "paketname",
        "Paket-Projektleiter": "paket_projektleiter",
        "Bemerkung": "bemerkung",
        "Paket-Status": "paket_status"
    }
    assert Constants.COLUMNS_TEMPLATE == expected_columns

def test_db_secret_name():
    assert Constants.DB_SECRET_NAME == os.environ.get("secret_name"), "DB_SECRET_NAME should match the environment variable"

def test_db_name():
    assert Constants.DB_NAME == os.environ.get("dbname"), "DB_NAME should match the environment variable"

def test_username():
    assert Constants.USERNAME == os.environ.get("username"), "USERNAME should match the environment variable"

def test_host():
    assert Constants.HOST == os.environ.get("host"), "HOST should match the environment variable"

def test_port():
    expected_port = os.environ.get("port", "5432")
    assert Constants.PORT == expected_port, "PORT should match the environment variable or default to 5432"

def test_drive_template_table_name():
    assert Constants.DRIVE_TEMPLATE_TABLE_NAME == "basic_data_drive_template"

def test_drive_content_table_name():
    assert Constants.DRIVE_CONTENT_TABLE_NAME == "basic_data_drive_contents"

def test_drive_table_name():
    assert Constants.DRIVE_TABLE_NAME == "basic_data_hu_marketvariant"

def test_sub_table_name():
    assert Constants.SUB_TABLE_NAME == "basic_data_hu_variant"

def test_log_table_name():
    assert Constants.LOG_TABLE_NAME == "basic_data_logs"

def test_aws_region():
    assert Constants.AWS_REGION == os.environ.get("region"), "AWS_REGION should match the environment variable"

def test_teams_webhook_secret_name():
    assert Constants.TEAMS_WEBHOOK_SECRET_NAME == os.environ.get("teams_webhook_secret_name"), "TEAMS_WEBHOOK_SECRET_NAME should match the environment variable"

def test_datadog_service_name():
    assert Constants.DATADOG_SERVICE_NAME == "basic-data-service"

def test_datadog_function_name():
    assert Constants.DATADOG_FUNCTION_NAME == "n-hu-marketvariant-service"

def test_timestamp_format():
    assert Constants.TIMESTAMP_FORMAT == "%Y-%m-%d %H:%M:%S.%fZ"

def test_process_done():
    assert Constants.PROCESS_DONE == "successed"

def test_process_failed():
    assert Constants.PROCESS_FAILED == "failed"

def test_success_progress():
    assert Constants.SUCCESS_PROGRESS == "100%"

def test_error_progress():
    assert Constants.ERROR_PROGRESS == "0%"

def test_success_message():
    assert Constants.SUCCESS_MESSAGE == "- file has been proccessed successfully."

def test_failed_message():
    assert Constants.FAILED_MESSAGE == "- file has been failed."

def test_error_message():
    assert Constants.ERROR_MESSAGE == "Something went wrong while processing the file. Please contact support team."

def test_empty_data_message():
    assert Constants.EMPTY_DATA_MESSAGE == "The uploaded file has no data."
