from constants import Constants
from response_builder import ResponseBuilder
from custom_exception import AWSSecretException, GenericException, ColumnValidationException
import json
import os
import requests
from log import logger
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

logger = logger(service_name=Constants.DATADOG_SERVICE_NAME, lambda_function_name=Constants.DATADOG_FUNCTION_NAME)

def generate_success_response(file_name):
    message = f"{file_name} - {Constants.SUCCESS_ESSAGE_FILE_PROCESS} {Constants.PROCESS_DONE}"
    logger.info(f"Success response generated for {file_name}")
    response = ResponseBuilder(status_code=200, response={"message": message, "file_name": file_name})
    return response.generate_response()

def generate_error_report(file_name, exception):
    logger.error(f"Failure error message generated for {file_name}: {exception}")
    error_report = {
        "drive_name": Constants.DRIVE_NAME,
        "file_name": file_name,
        "environment": Constants.ENVIRONMENT,
        "error_report": []
    }
    error_report["status"] = Constants.PROCESS_FAILED
    error_report["progress"] = Constants.ERROR_PROGRESS
    error_report["created_timestamp"] = (datetime.now()).strftime(Constants.TIMESTAMP_FORMAT)
    try:
        error_report["error_report"] = [{"error_message": exception.message}]
    except Exception as e:
        logger.error(f"Error in generating error report: {e}")
    return error_report

def get_secret_dict(secret_name):
    """
    Retrieve the secret value from AWS Secrets Manager.
    """
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=Constants.AWS_REGION
    )
    
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        return get_secret_value_response
    except ClientError as e:
        logger.error(f"Error retrieving secret {secret_name}: {e}")
        raise AWSSecretException(f"Error retrieving secret {secret_name}. Please contact to dev team.")
    
def send_teams_message(msg, result):
    if os.environ.get("ENV") != "TEST":
        secret_name = Constants.TEAMS_WEBHOOK_SECRET_NAME
        teams_webhook_secret = get_secret_dict(secret_name)
        teams_webhook_response = json.loads(teams_webhook_secret['SecretString'])
        url = teams_webhook_response["webhook_url"]
        context_url = teams_webhook_response["context_url"]
        webhook_message = teams_webhook_response["webhook_message"]

        message = json.loads(webhook_message)
        message["@context"] = str(context_url)
        message["sections"][0]["activityTitle"] = result.get("drive_name")
        message["sections"][0]["activitySubTitle"] = msg
        message["sections"][0]["facts"][0]["value"] = result.get("progress")
        message["sections"][0]["facts"][1]["value"] = result.get("status")
        message["sections"][0]["facts"][2]["value"] = result.get("environment")
        message["sections"][0]["facts"][3]["value"] = result.get("error_report")

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(message))
            if response.status_code != 200:
                logger.error(f"Failed to send message to Teams: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending message to Teams: {e}")
            raise GenericException(f"Error sending message to Teams.") 
        
def validate_column_template(column_template, df):
    try:
        # Strip all dataframe column name
        df.columns = df.columns.str.strip()

        # Identify missing columns
        missing_columns = [col for col in column_template.keys() if col not in df.columns]

        # Identify extra columns
        extra_columns = [col for col in df.columns if col not in column_template.keys()]

        # Raise error if missing or extra columns exists
        if missing_columns or extra_columns:
            error_message = []
            if missing_columns:
                error_message.append(f"Missing columns: {missing_columns}")
            if extra_columns:
                error_message.append(f"Extra columns: {extra_columns}")

            user_message = (
                "Column validation failed. " +
                " ".join(error_message) +
                " Please upload the correct sheet again."
            )
            logger.error(user_message)
            raise ColumnValidationException(user_message)
        else:
            logger.info("All required columns are present and no extra columns found.")
    except Exception as e:
        logger.error(f"Error validating columns: {e}")
        raise
    
