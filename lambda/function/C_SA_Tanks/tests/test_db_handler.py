import pytest
from unittest.mock import patch, MagicMock
from src.db_handler import get_column_template
from src.custom_exception import GenericException

@patch("src.db_handler.Database")
def test_get_column_template_success(mock_database):
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"drive_column_name": "mock_column"}
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_database.return_value.get_connection.return_value.__enter__.return_value = mock_conn

    # Call the function
    result = get_column_template()

    # Assertions
    assert result == {"drive_column_name": "mock_column"}
    mock_cursor.execute.assert_called_once()
    mock_cursor.fetchone.assert_called_once()
    mock_database.return_value.release_connection.assert_called_once()

@patch("db_handler.Database")
def test_get_column_template_exception(mock_database):
    # Mock the database to raise an exception
    mock_database.return_value.get_connection.side_effect = Exception("Database error")

    # Call the function and assert it raises the correct exception
    with pytest.raises(GenericException, match="Error fetching column templates: Database error"):
        get_column_template()

    mock_database.return_value.release_connection.assert_called_once()