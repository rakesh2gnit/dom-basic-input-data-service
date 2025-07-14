import os
from urllib.parse import unquote_plus
from compare_df import data_compare
from custom_exception import GenericException
from constants import Constants
from log import logger as logger_factory
import utils
import db_handler

# Logger setup
logger = logger_factory(
    service_name=Constants.DATADOG_SERVICE_NAME,
    lambda_function_name=Constants.DATADOG_FUNCTION_NAME
)

def log_and_notify(file_name, message, payload):
    db_handler.insert_data_log_api(payload)
    utils.send_teams_message(f"{file_name} - {message}", payload)

# Parse S3 event
def parse_s3_event(event):
    record = event['Records'][0]
    file_key = unquote_plus(record['s3']['object']['key'])
    bucket_name = record['s3']['bucket']['name']
    file_name = unquote_plus(os.path.basename(file_key))
    return file_key, bucket_name, file_name

def lambda_handler(event, context):
    
    file_key, bucket_name, file_name = parse_s3_event(event)

    try:
        logger.info(f"Processing file: {file_name} from bucket: {bucket_name}")

        # Process the file
        result = data_compare(bucket_name, file_key)

        # Log and notify success
        log_and_notify(file_name, Constants.SUCCESS_MESSAGE, result)
        logger.info(f"File {file_name} processed successfully")

        return result

    except GenericException as e:
        logger.warning(Constants.GENERIC_ERROR_MSG)
        error_report = utils.generate_error_report(file_name, e)
        log_and_notify(file_name, Constants.FAILED_MESSAGE, error_report)
        return error_report

    except Exception as e:
        logger.error(Constants.UNKNOWN_ERROR_MSG, exc_info=True)
        error_report = utils.generate_error_report(file_name, e)
        log_and_notify(file_name, Constants.FAILED_MESSAGE, error_report)
        return error_report