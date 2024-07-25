from extraction_logic import manipulate_dataframe
from extraction_logic import download_read_s3_file

import pandas as pd
import pytest
import boto3
import tempfile
import os
import numpy as np

#pytest --cov=extraction_logic --cov-report=html

@pytest.fixture
def sample_excel_path():
    return '/Users/rakeshkumar/AndroidStudioProjects/dom-basic-input-data-service/lambda/function/H_Berichte/src/tests/AJ-Bericht_PKW_2024-03_AJ2024_AJ2025_AJ2026_1.xlsx'

@pytest.fixture
def sample_excel_dataframe(sample_excel_path):
    return pd.read_excel(sample_excel_path)

def test_manipulate_dataframe_rename_columns(sample_excel_dataframe):
    # Test case to check if columns are renamed correctly
    expected_df = pd.DataFrame({
        'br': ['C118','C118'],
        'aa': ['FC', 'FC'],
        'aj_mopf': ['AJ', 'AJ'],
        'aj_paket': ['AJ2024/2', 'AJ2024/2'],
        'paket_pu_termin': pd.to_datetime(['2024/09/01', '2024/09/01']),
        'paketname': ['AJ2024/2-C118, AJ2024 2', 'AJ2024/2-C118, AMG'],
        'paket_projektleiter': ['Raith, Melanie, RD/VCS', 'Schoellmann, Dominik, GRC/PSVP'],
        'bemerkung': [np.nan, np.nan],
        'paket_status': ['Freigegeben', 'Freigegeben']
    })

    # Call the function under test
    output_df = manipulate_dataframe(sample_excel_dataframe)
    
    # Assert that the output matches the expected dataframe
    pd.testing.assert_frame_equal(output_df, expected_df)

# Mock boto3 S3 client and resource
@pytest.fixture
def mock_boto3():
    class MockS3Client:
        def download_file(self, bucket, key, filename):
            with open(filename, 'w') as f:
                f.write("Mock Excel Data")

    class MockS3Resource:
        def Bucket(self, bucket_name):
            return MockS3Client()

    original_boto3_client = boto3.client
    original_boto3_resource = boto3.resource

    boto3.client = lambda service: MockS3Client()
    boto3.resource = lambda service: MockS3Resource()

    yield

    boto3.client = original_boto3_client
    boto3.resource = original_boto3_resource

# Test cases

def test_download_read_s3_file_file_not_found(mock_boto3):
    s3_bucket_name = "mock_bucket"
    s3_file_name = "non_existing_file.xlsx"

    result = download_read_s3_file(s3_bucket_name, s3_file_name)

    assert result is None


