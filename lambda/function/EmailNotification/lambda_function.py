import boto3
from botocore.exceptions import ClientError
import os
import json
from template import *
from utils import *
from datetime import datetime
from constants import Constants

def get_secret():
    secret_name = os.environ['EMAIL_SECRET']
    region_name = os.environ['REGION']

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return secret

def lambda_handler(event, context):
    secret = json.loads(get_secret())
    file_time = event.get('datetime', None)
    drive_name = event.get('drive_name', None)
    file_name = event.get('file_name', None)
    upload_status = event.get('status', None)

    dt = datetime.strptime(file_time, Constants.DATETIME_FORMAT)
    # Custom readable format
    readable_datetime = dt.strftime("%B %d, %Y at %I:%M %p")

    SMTP_SERVER = secret['SMTP_SERVER']
    SMTP_USERNAME = secret['SMTP_USERNAME']
    SMTP_PASSWORD = secret['SMTP_PASSWORD']
    EMAIL_SENDER = secret['EMAIL_SENDER']
    EMAIL_RECEIVER = secret['EMAIL_RECEIVER']

    if isinstance(EMAIL_RECEIVER, str):
        EMAIL_RECEIVER = EMAIL_RECEIVER.split(',')

    is_success = upload_status == Constants.SUCCESS_MESSAGE

    HTML_TEMPLATE = html_template.format(
        title = "Operation Triggered",
        status_icon = "✅" if is_success else "❌",
        header = "Basic Input Data - Operation Triggered",
        message = "Hello,<br/><br/>The file upload operation has been completed successfully." if is_success else "Hello,<br/><br/>The file upload operation has failed.",
        date = readable_datetime,
        drive_name = drive_name,
        file_name = file_name,
        link = "https://console.aws.amazon.com/s3/home",
        sender = "Your Automation System"
        footer = "c 2025 | Do not reply to this email."
    )

    send_email(SMTP_SERVER, 25, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_SENDER, EMAIL_RECEIVER, HTML_TEMPLATE)
