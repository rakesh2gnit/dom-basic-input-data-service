import boto3
import pandas as pd
from io import BytesIO
import openpyxl
from custom_exception import BadRequestException

def read_file_from_s3(bucket_name, file_key):
    try:
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read()

        df = pd.read_excel(BytesIO(file_content))
        wb = openpyxl.load_workbook(filename=BytesIO(file_content), read_only=True)
        sheet = wb.active
        return df, sheet
    except Exception as e:
        print(f"File not found in S3 bucket: {bucket_name}/{file_key}")
        raise BadRequestException(f"Error while reading the file: {e}") from e