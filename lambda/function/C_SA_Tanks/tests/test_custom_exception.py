from src.constants import Constants
from src.custom_exception import GenericException, DatabaseException

def test_generic_exception():
    exception = GenericException(500, "An error occurred")

    assert exception.error_message == "An error occurred"
    assert exception.status_code == 500

def test_database_exception():
    exception = DatabaseException("Database connection failed")

    assert exception.error_message == "Database connection failed"
    assert exception.status_code == 502