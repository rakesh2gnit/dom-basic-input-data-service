from constants import Constants
import boto3
import pandas as pd
import numpy as np
from io import BytesIO
import openpyxl
import db_handler
import os
from utils import validate_column_template
from datetime import datetime
from log import logger
from custom_exception import BadRequestException, EmptyDataException, RowValidationException

logger = logger(
    service_name=Constants.DATADOG_SERVICE_NAME, 
    lambda_function_name=Constants.DATADOG_FUNCTION_NAME
    )

def data_compare(bucket_name, file_path):
    df, sheet = read_file_from_s3(bucket_name, file_path)
    file_name = os.path.basename(file_path)

    if df.empty:
        logger.error(f"{file_name} - The uploaded file has no data.")
        raise EmptyDataException(f"{file_name} - The uploaded file has no data.")
 
    try:
        column_template = Constants.COLUMNS_TEMPLATE
        validate_column_template(column_template, df)

        result = db_handler.get_column_template()
        column_template = result[0] if result else column_template

        if not result:
            logger.info("No column template found for this drive")
            db_handler.load_drive_template()

        df.columns = df.columns.str.strip()
        df.rename(columns=column_template, inplace=True)
        df.drop_duplicates(inplace=True)

        df = data_transform(df, sheet, key_columns=["aj_paket", "paket_pu_termin"])
        df.drop_duplicates(subset='key', inplace=True)

        df, error_object = data_validate(df)
        df["additional_data"] = None
        df["file_name"] = file_name

        columns_to_insert = list(column_template.values()) + ['key', 'file_name', 'status']
        db_file_names = db_handler.get_existing_file_name()['file_name'].values

        if file_name not in db_file_names:
            db_handler.load_drive_content(file_name, file_path)

        df_database = db_handler.get_drive_table_data(columns_to_insert)

        # info = []

        df['updated'] = datetime.now()
        columns_to_insert.append('updated')

        update_database(df, df_database, columns_to_insert)

        return {
            "drive_name": Constants.DRIVE_NAME,
            "file_name": file_name,
            "environment": Constants.ENVIRONMENT,
            "status": Constants.PROCESS_DONE,
            "progress": Constants.SUCCESS_PROGRESS,
            "created_timestamp": datetime.now().strftime(Constants.TIMESTAMP_FORMAT),
            "error_report": error_object,
            "info": []
        }
    except Exception as e:
        logger.error(f"Internal Server Error. {e}")
        raise
    
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

def read_file_from_s3(bucket_name, file_key):
    try:
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read()

        df = pd.read_excel(BytesIO(file_content), engine = "openpyxl")
        wb = openpyxl.load_workbook(BytesIO(file_content))
        sheet = wb.active
        return df, sheet
    except Exception as e:
        logger.error(f"File not found in S3 bucket: {bucket_name}/{file_key} : {e}")
        raise BadRequestException(f"Error while reading the file.")
    
def data_transform(df, sheet, key_columns):
    try:
        df = df.dropna(how='all')  # Drop rows where all key columns are NaN
        df.replace({np.nan: None, pd.NaT: None}, inplace=True)  # Replace NaN and NaT with None

        if sheet:
            color_check = []
            for row in sheet.iter_rows(min_row=2, max_row=df.shape[0] + 1):
                cell = row[2]
                if cell.font.color:
                    font_color = cell.font.color.rgb
                else:
                    font_color = None
                if font_color == "FF00B050":
                    color_check.append(2)  # Green
                elif font_color in ("FFFF0000", "FFC00000"):
                    color_check.append(1)  # Red
                else:
                    color_check.append(3)  # No color
            df["status"] = color_check
            df['status'] = pd.to_numeric(df['status'], errors='coerce').astype('int')
            
        df['key'] = df.apply(lambda row: "_".join(map(str, [row[col] for col in key_columns])), axis=1)
        return df
    except Exception as e:
        logger.error(f"Error in data transformation: {e}")
        raise BadRequestException(f"Error in data transformation.")
    
def data_validate(df):
    df.replace({np.nan: None, pd.NaT: None}, inplace=True)

    missing_entries = []
    invalid_entries = []
    indexes = []

    for index, row in df.iterrows():
        missing_columns = []
        invalid_columns = []
        if row['aj_paket'] is None:
            missing_columns.append("aj_paket")
            indexes.append(index)
        if row['paket_pu_termin'] is None:
            missing_columns.append("paket_pu_termin")
            indexes.append(index)

        if missing_columns:
            missing_entries.append({
                "row": index+2,
                "columns": missing_columns
            })

        if invalid_columns:
            invalid_entries.append({
                "row": index+2,
                "columns": invalid_columns
            })

    messages = []

    if missing_entries:
        messages.append(
            "Some required fields are missing in the uploaded file. "
            "Missing values found: "
            f"{missing_entries}. Please make sure all required fields are filled, as defined in the template."
        )

    if invalid_entries:
        messages.append(
            "Some required fields are invalid in the uploaded file. "
            "Invalid values found: "
            f"{invalid_entries}. Please make sure all required fields are valid, as defined in the template."
        )

    if messages:
        user_message = "\n".join(messages)
        logger.error(user_message)
        raise RowValidationException(user_message)
    else:
        logger.info("All required rows are present.")
        if indexes:
            df.drop(indexes, inplace=True)
        return df, invalid_entries