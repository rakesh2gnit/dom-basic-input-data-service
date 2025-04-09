from constants import Constants
from response_builder import ResponseBuilder
from custom_exception import GenericException
import json
import os
import requests
from log import logger
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

logger = logger(service_name=Constants.DATADOG_SERVICE_NAME, lambda_function_name=Constants.DATADOG_FUNCTION_NAME)

def generate_success_response(file_name):
    message = f"{file_name} - {Constants.SUCCESS_MESSAGE}"
    logger.info(f"Success response generated for {file_name}")
    response = ResponseBuilder(status_code=200, response={"message": message, "file_name": file_name})
    return response.generate_response()

def generate_fail_response(file_name, exception: GenericException):
    message = f"{file_name} - {Constants.FAILURE_MESSAGE}"
    logger.error(f"Failure response generated for {file_name}: {exception}")
    response = ResponseBuilder(status_code=500, response={"message": message, "file_name": file_name})
    error_report = {
        "drive_name": Constants.DRIVE_NAME,
        "file_name": file_name,
        "status": Constants.PROCESS_FAILED,
        "progress": Constants.ERROR_PROGRESS,
        "environment": Constants.ENVIRONMENT,
        "created_timestamp": datetime.now().strftime(Constants.DATE_FORMAT),
        "error_message": str(exception)
    }
    return response.generate_response()

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
        raise GenericException(f"Error retrieving secret {secret_name}: {e}") from e
    
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
            raise GenericException(f"Error sending message to Teams: {e}") from e
