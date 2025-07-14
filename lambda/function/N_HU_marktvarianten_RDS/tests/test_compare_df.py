import pytest
import pandas as pd
from types import SimpleNamespace
from src.compare_df import data_validate, RowValidationException

# Mock Constants.COLUMNS_TEMPLATE
@pytest.fixture
def column_template():
    return {
        "col1": "col1_new",
        "aj_paket": "aj_paket",
        "paket_pu_termin": "paket_pu_termin"
    }

# Dummy DataFrame fixture
@pytest.fixture
def valid_dataframe():
    return pd.DataFrame({
        "aj_paket": ["A1", "A2"],
        "paket_pu_termin": ["T1", "T2"],
        "col1": [1, 2]
    })

def test_data_validate_success(valid_dataframe):
    df, errors = data_validate(valid_dataframe)
    assert errors == []
    assert not df.empty

def test_data_validate_missing_column(valid_dataframe):
    valid_dataframe.loc[0, "aj_paket"] = None
    with pytest.raises(RowValidationException) as exc_info:
        data_validate(valid_dataframe)
    assert "Missing values found" in str(exc_info.value)

def test_data_validate_success():
    df = pd.DataFrame({
        "aj_paket": ["A1", "A2"],
        "paket_pu_termin": ["T1", "T2"]
    })

    cleaned_df, errors = data_validate(df.copy())
    assert not errors
    assert len(cleaned_df) == 2


def test_data_validate_missing_columns():
    df = pd.DataFrame({
        "aj_paket": [None, "A2"],
        "paket_pu_termin": ["T1", None]
    })

    with pytest.raises(RowValidationException) as excinfo:
        data_validate(df.copy())

    assert "Missing values found" in str(excinfo.value)

def mock_sheet_with_colors(colors):
    class Font:
        def __init__(self, rgb):
            self.color = SimpleNamespace(rgb=rgb) if rgb else None

    class Cell:
        def __init__(self, rgb):
            self.font = Font(rgb)

    class Row:
        def __init__(self, rgb):
            self.cells = [None, None, Cell(rgb)]
        def __getitem__(self, index):
            return self.cells[index]

    class Sheet:
        def iter_rows(self, min_row, max_row):
            return [Row(rgb) for rgb in colors]

    return Sheet()