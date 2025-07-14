from constants import Constants
from custom_exception import AWSSecretException, GenericException, ColumnValidationException
import json
import os
import requests
from log import logger
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

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
    

def send_teams_message(msg: str, result: dict) -> None:
    if os.environ.get("ENV") == "TEST":
        return  # Avoid sending real notifications during tests

    try:
        secrets = get_secret_dict(Constants.TEAMS_WEBHOOK_SECRET_NAME)
        webhook_data = json.loads(secrets["SecretString"])

        message = json.loads(webhook_data["webhook_message"])
        message["@context"] = str(webhook_data["context_url"])
        message["sections"][0]["activityTitle"] = result.get("drive_name")
        message["sections"][0]["activitySubTitle"] = msg
        message["sections"][0]["facts"][0]["value"] = result.get("progress")
        message["sections"][0]["facts"][1]["value"] = result.get("status")
        message["sections"][0]["facts"][2]["value"] = result.get("environment")
        message["sections"][0]["facts"][3]["value"] = result.get("error_report")

        response = requests.post(
            webhook_data["webhook_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(message)
        )

        if response.status_code != 200:
            logger.error(f"[Teams] Failed to send message: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        logger.error(f"[Teams] Request error: {e}")
        raise GenericException("Error sending message to Teams.")
    except Exception as e:
        logger.error(f"[Teams] Unexpected error: {e}")
        raise GenericException("Unexpected error in Teams message logic.")
    

def validate_column_template(column_template: dict, df) -> None:
    try:
        df.columns = df.columns.str.strip()
        missing_column = [col for col in column_template.keys() if col not in df.columns]
        extra_columnm = [col for col in df.columns if col not in column_template.keys()]

        if missing_column or extra_columnm:
            messages = []
            if missing_column:
                messages.append(f"Missing columns: {missing_column}")
            if extra_columnm:
                messages.append(f"Extra columns: {extra_columnm}")
            error_msg = "Column validation failed. " + " ".join(messages) + " Please upload the correct sheet again."
            logger.error(f"[Validation] {error_msg}")
            raise ColumnValidationException(error_msg)

        logger.info("[Validation] Column structure is valid.")

    except Exception as e:
        logger.error(f"[Validation] Error validating columns: {e}")
        raise