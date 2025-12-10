from constants import Constants
from custom_exception import AWSSecretException, GenericException, ColumnValidationException
import json
import os
import requests
from log import logger
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
from datetime import date, datetime


# Initialize logger
logger = logger(
    service_name=Constants.DATADOG_SERVICE_NAME, 
    lambda_function_name=Constants.DATADOG_FUNCTION_NAME
    )

def generate_error_report(file_name: str, exception: Exception) -> dict:
    logger.error(f"[Error Report] Failure for {file_name}: {exception}")
    error_report = {
        "drive_name": Constants.DRIVE_NAME,
        "file_name": file_name,
        "environment": Constants.ENVIRONMENT,
        "status": Constants.PROCESS_FAILED,
        "progress": Constants.ERROR_PROGRESS,
        "created_timestamp": datetime.now().strftime(Constants.TIMESTAMP_FORMAT),
        "error_report": []
    }
    try:
        error_report["error_report"] = [{"error_message": getattr(exception, "message", str(exception))}]
    except Exception as e:
        logger.error(f"[Error Report] Failed to extract error message: {e}")
    return error_report

def get_secret_dict(secret_name: str) -> dict:
    try:
        session = boto3.session.Session()
        client = session.client("secretsmanager", region_name=Constants.AWS_REGION)
        response = client.get_secret_value(SecretId=secret_name)
        return response
    except ClientError as e:
        logger.error(f"[Secrets] Error retrieving secret {secret_name}: {e}")
        raise AWSSecretException(f"Error retrieving secret {secret_name}. Please contact the dev team.")
    
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime) or isinstance(obj, date):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)