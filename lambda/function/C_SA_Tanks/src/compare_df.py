from constants import Constants
import db_handler
import data_processing
from datetime import datetime
import ast
from log import logger

logger = logger(service_name=Constants.DATADOG_SERVICE_NAME, lambda_function_name=Constants.DATADOG_FUNCTION_NAME)

def data_compare(df, sheet, file_name, file_path):
    error_report = {
        "drive_name": Constants.DRIVE_NAME,
        "file_name": file_name,
        "environment": Constants.ENVIRONMENT,
        "error_report": []
    }
    try:
        column_template = Constants.COLUMNS_TEMPLATE

        result = db_handler.get_column_template()

        if result:
            column_template = result[0]
        else:
            logger.info(f"No column template fond for this drive")
            db_handler.load_drive_template()

        db_file_name = db_handler.get_existing_file_name()

        if file_name not in db_file_name['file_name'].values:
            db_handler.load_drive_content(file_name, file_path)

        df = data_processing.data_transform(df, sheet, column_template)

        df["additional_data"] = None
        df["file_name"] = file_name

        columns_to_insert = list(column_template.values() + ['key', 'file_name', 'status'])

        df_database = db_handler.get_sa_tank_data(columns_to_insert)

        info = []

        df['updated'] = datetime.now()
        columns_to_insert.append('updated')

        update_database(df, df_database, columns_to_insert)

        error_report["status"] = Constants.PROCESS_DONE
        error_report["progress"] = Constants.SUCCESS_PROGRESS
        error_report["created_timestamp"] = (datetime.now()).strftime(Constants.TIMESTAMP_FORMAT)
        error_report["error_report"] = error_object
        error_report["info"] = info

        db_handler.insert_data_log_api(error_report)
        return error_report
    except Exception as e:
        error_report["status"] = Constants.PROCESS_FAILED
        error_report["progress"] = Constants.ERROR_PROGRESS
        error_report["created_timestamp"] = (datetime.now()).strftime(Constants.TIMESTAMP_FORMAT)
        error_report["error_report"] = [{"message":"something went wrong. Please check the logs"}]
        error_report["info"] = info
        db_handler.insert_data_log_api(error_report)
        raise e
    
def update_database(df, df_database, columns_to_insert):
    columns_to_insert = columns_to_insert + ['action', 'changes']

    df_to_update = df[df['key'].isin(df_database['key'])]
    df_to_insert = df[~df['key'].isin(df_database['key'])]

    df_to_update['action'] = None
    df_to_update['chnages'] = None

    df_to_insert['action'] = "insert"
    df_to_insert['changes'] = None

    db_handler.update_sa_tank_data(df_database, df_to_update, columns_to_insert)

    db_handler.insert_sa_tank_data(df_to_insert, columns_to_insert)


