from compare_df import data_compare
from urllib.parse import unquote_plus
from custom_exception import GenericException
import os
from log import logger
from constants import Constants
import utils
import db_handler

logger = logger(service_name=Constants.DATADOG_SERVICE_NAME, lambda_function_name=Constants.DATADOG_FUNCTION_NAME)

def lambda_handler(event, context):
    file_key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = unquote_plus(os.path.basename(file_key))

    try:
        logger.info(f"Processing file: {file_name} from bucket: {bucket_name}")
        result = data_compare(bucket_name, file_key)
        db_handler.insert_data_log_api(result)
        message = f"{file_name} - {Constants.SUCCESS_MESSAGE}"
        utils.send_teams_message(message, result)
        logger.info(f"File {file_name} processed successfully")
        return result
    except GenericException as e:
        print("===GenericException===")
        error_report = utils.generate_error_report(file_name, e)
        db_handler.insert_data_log_api(error_report)
        message = f"{file_name} - {Constants.FAILED_MESSAGE}"
        utils.send_teams_message(message, error_report)
        return error_report
    except Exception as e:
        print("===Exception===")
        error_report = utils.generate_error_report(file_name, e)
        db_handler.insert_data_log_api(error_report)
        message = f"{file_name} - {Constants.FAILED_MESSAGE}"
        utils.send_teams_message(message, error_report)
        return error_report