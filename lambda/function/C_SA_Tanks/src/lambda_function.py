from file_processing import read_file_from_s3
from compare_df import data_compare
from urllib.parse import unquote_plus
import os
from log import logger
from constants import Constants
import utils
import db_handler

logger = logger(service_name=Constants.DATADOG_SERVICE_NAME, lambda_function_name=Constants.DATADOG_FUNCTION_NAME)

def lambda_handler(event, context):
    file_key = event['Records'][0]['s3']['object']['key']
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = unquote_plus(os.path.basename(file_key))

    try:
        logger.info(f"Processing file: {file_name} from bucket: {bucket_name}")
        df, sheet = read_file_from_s3(bucket_name, file_key)
        result = data_compare(df, sheet, file_name, file_key)
        message = f"{file_name} - {Constants.SUCCESS_MESSAGE}"
        utils.send_teams_message(message, result)
        logger.info(f"File {file_name} processed successfully")
        return result
    except Exception as e:
        error_report = utils.generate_fail_response(file_name, e)
        message = f"{file_name} - {Constants.FAILED_MESSAGE}"
        db_handler.insert_data_log_api(error_report)
        utils.send_teams_message(message, error_report)
        return error_report