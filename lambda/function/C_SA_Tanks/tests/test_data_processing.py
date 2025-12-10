import pytest
from src.data_processing import data_transform
from unittest.mock import MagicMock
from src.custom_exception import BadRequestException
from unittest.mock import patch

def test_data_transform(mocker):
    """Test the data_transform function."""
    # Mock the DataFrame and sheet
    mock_df = mocker.Mock()
    mock_sheet = mocker.Mock()
    
    # Mock the column templates
    column_templates = {
        'old_column_name': 'new_column_name'
    }

    # Mock the DataFrame columns
    mock_df.columns = mocker.Mock()
    mock_df.columns.str = mocker.Mock()
    mock_df.columns.str.strip = mocker.Mock()

    mock_df.rename = mocker.Mock()
    mock_df.drop_duplicates = mocker.Mock()
    mock_df.dropna = mocker.Mock()
    mock_df.replace = mocker.Mock()
    mock_df.apply = mocker.Mock()

    # Call the function
    result = data_transform(mock_df, mock_sheet, column_templates)

    # Assertions
    assert result is not None
    mock_df.columns.str.strip.assert_called_once()
    mock_df.rename.assert_called_once_with(columns=column_templates, inplace=True)
    