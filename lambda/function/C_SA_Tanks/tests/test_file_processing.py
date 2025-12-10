import boto3
import pytest
import pandas as pd
from io import BytesIO

from moto import mock_aws  # ✅ New way for Moto v5+
from src.file_processing import read_file_from_s3  # replace with your actual module


@pytest.fixture
def sample_excel_file():
    df = pd.DataFrame({
        'Name': ['Alice', 'Bob'],
        'Age': [30, 25]
    })
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output.read()

@mock_aws(service_name="s3")  # ✅ Correct usage for Moto v5+
def test_read_file_from_s3_success(sample_excel_file):
    bucket_name = "test-bucket"
    file_key = "test.xlsx"

    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=bucket_name)
    s3.put_object(Bucket=bucket_name, Key=file_key, Body=sample_excel_file)

    df, sheet = read_file_from_s3(bucket_name, file_key)

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert df.columns.tolist() == ["Name", "Age"]
    assert sheet.title == "Sheet1"