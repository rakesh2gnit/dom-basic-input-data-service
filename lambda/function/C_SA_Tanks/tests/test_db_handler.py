import pytest
# from unittest.mock import patch, MagicMock
from src.db_handler import get_column_template
from src.custom_exception import BadRequestException

def test_get_column_template(mocker):
    expected_result = {"drive_column_name": "mock_column"}

    # Mock the cursor
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.return_value = expected_result

    # Mock the connection
    mock_conn = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Mock the Database instance
    mock_db_instance = mocker.MagicMock()
    
    # 👇 Key fix here: get_connection().__enter__() should return mock_conn
    mock_get_conn = mocker.MagicMock()
    mock_get_conn.__enter__.return_value = mock_conn
    mock_db_instance.get_connection.return_value = mock_get_conn

    # Patch Database to return our mock instance
    mocker.patch('src.db_handler.Database', return_value=mock_db_instance)

    # Act
    result = get_column_template()

    # Assert
    assert result == expected_result
    mock_db_instance.get_connection.assert_called_once()
    mock_db_instance.release_connection.assert_called_once_with(mock_conn)



# @patch("src.db_handler.Database")
# def test_get_column_template_success(mock_database):
#     # Mock the database connection and cursor
#     mock_conn = MagicMock()
#     mock_cursor = MagicMock()
#     mock_cursor.fetchone.return_value = {"drive_column_name": "mock_column"}
#     mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
#     mock_database.return_value.get_connection.return_value.__enter__.return_value = mock_conn

#     # Call the function
#     result = get_column_template()

#     # Assertions
#     assert result == {"drive_column_name": "mock_column"}
#     mock_cursor.execute.assert_called_once()
#     mock_cursor.fetchone.assert_called_once()
#     mock_database.return_value.release_connection.assert_called_once()

# @patch("db_handler.Database")
# def test_get_column_template_exception(mock_database):
#     # Mock the database to raise an exception
#     mock_database.return_value.get_connection.side_effect = Exception("Database error")

#     # Call the function and assert it raises the correct exception
#     with pytest.raises(GenericException, match="Error fetching column templates: Database error"):
#         get_column_template()

#     mock_database.return_value.release_connection.assert_called_once()
# @patch("src.db_handler.Database")
# def test_get_column_template_success(mock_database):
#     # Mock the database connection and cursor
#     mock_conn = MagicMock()
#     mock_cursor = MagicMock()
#     mock_cursor.fetchone.return_value = {"drive_column_name": "mock_column"}
#     mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
#     mock_database.return_value.get_connection.return_value.__enter__.return_value = mock_conn

#     # Call the function
#     result = get_column_template()

#     # Assertions
#     assert result == {"drive_column_name": "mock_column"}
#     mock_cursor.execute.assert_called_once()
#     mock_cursor.fetchone.assert_called_once()
#     mock_database.return_value.release_connection.assert_called_once()

# @patch("src.db_handler.Database")
# def test_get_column_template_exception(mock_database):
#     # Mock the database to raise an exception
#     mock_database.return_value.get_connection.side_effect = Exception("Database error")

#     # Call the function and assert it raises the correct exception
#     with pytest.raises(BadRequestException, match="Error fetching column templates: Database error"):
#         get_column_template()

#     mock_database.return_value.release_connection.assert_not_called()