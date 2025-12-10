import pytest
import pandas as pd
from types import SimpleNamespace
from src.compare_df import data_validate, RowValidationException, data_transform, BadRequestException, read_file_from_s3

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

def test_data_validate_empty_df():
    df = pd.DataFrame(columns=["aj_paket", "paket_pu_termin"])
    cleaned_df, errors = data_validate(df)
    assert cleaned_df.empty
    assert errors == []

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

def test_data_transform_raises_bad_request(monkeypatch):
    df = pd.DataFrame({
        "aj_paket": [None],
        "paket_pu_termin": [None]
    })

    # Passing a sheet that raises an exception inside the loop
    class BadSheet:
        def iter_rows(self, min_row, max_row):
            raise Exception("Corrupt sheet")

    with pytest.raises(BadRequestException) as exc:
        data_transform(df.copy(), BadSheet(), key_columns=["aj_paket", "paket_pu_termin"])

    assert "Error in data transformation" in str(exc.value)

def test_read_file_from_s3(monkeypatch):
    import io
    import openpyxl

    df = pd.DataFrame({"aj_paket": [1], "paket_pu_termin": [2]})
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    stream.seek(0)
    file_content = stream.read()

    class DummyS3:
        def get_object(self, Bucket, Key):
            return {"Body": io.BytesIO(file_content)}

    monkeypatch.setattr("src.compare_df.boto3.client", lambda service: DummyS3())
    df_result, sheet = read_file_from_s3("bucket", "file.xlsx")
    
    assert not df_result.empty
    assert sheet is not None

def test_read_file_from_s3_failure(monkeypatch):
    class DummyS3:
        def get_object(self, Bucket, Key):
            raise Exception("File not found")

    monkeypatch.setattr("src.compare_df.boto3.client", lambda service: DummyS3())

    with pytest.raises(BadRequestException) as exc:
        read_file_from_s3("bucket", "file.xlsx")

    assert "Error while reading the file" in str(exc.value)

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