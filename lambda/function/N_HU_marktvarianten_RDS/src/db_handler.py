from constants import Constants
from datetime import datetime
from database import Database
import pandas as pd
import numpy as np
import json
from custom_exception import DatabaseException
from log import logger

logger = logger(service_name=Constants.DATADOG_SERVICE_NAME, lambda_function_name=Constants.DATADOG_FUNCTION_NAME)

# --- Utility functions ---

def run_query(query, params=None, fetch="all", to_df_columns=None):
    db = Database()
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if fetch == "one":
                    return cursor.fetchone()
                elif fetch == "all":
                    return cursor.fetchall() if not to_df_columns else pd.DataFrame(cursor.fetchall(), columns=to_df_columns)
                elif fetch == "insert":
                    inserted_id = cursor.fetchone()[0]
                    conn.commit()
                    return inserted_id
                elif fetch == "none":
                    conn.commit()
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        raise DatabaseException("Database operation failed. Please connect with dev team.")
    

def get_column_template():
    query = f"""
        SELECT drive_column_name
        FROM {Constants.DB_SCHEMA_NAME}.{Constants.DRIVE_TEMPLATE_TABLE_NAME}
        WHERE drive_name = %s
    """
    return run_query(query, (Constants.DRIVE_NAME,), fetch="one")


def load_drive_template():
    query = f"""
        INSERT INTO {Constants.DB_SCHEMA_NAME}.{Constants.DRIVE_TEMPLATE_TABLE_NAME}
        (drive_name, drive_type, drive_column_name, created_by, created_timestamp, updated_timestamp, version)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    params = (
        Constants.DRIVE_NAME,
        "",
        json.dumps(Constants.COLUMNS_TEMPLATE),
        "KUMRAK2",
        datetime.now(),
        datetime.now(),
        "v1"
    )
    return run_query(query, params, fetch="insert")


def get_existing_file_name():
    query = f"""
        SELECT file_name
        FROM {Constants.DB_SCHEMA_NAME}.{Constants.DRIVE_TEMPLATE_TABLE_NAME}
    """
    return run_query(query, fetch="all", to_df_columns=['file_name'])


def load_drive_content(file_name, file_path):
    query = f"""
        INSERT INTO {Constants.DB_SCHEMA_NAME}.{Constants.DRIVE_CONTENT_TABLE_NAME}
        (drive_type, file_name, s3_path, uploaded_by, result_log_path, created_timestamp,
         delete_timestamp, is_deleted, version)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    params = (
        "", file_name, file_path, "KUMRAK2", "None",
        datetime.now(), None, False, "v1"
    )
    return run_query(query, params, fetch="insert")


def get_drive_table_data(columns_to_insert):
    query = f"""
        SELECT {str(', '.join(columns_to_insert))}
        FROM {Constants.DB_SCHEMA_NAME}.{Constants.DRIVE_TABLE_NAME}
    """
    df = run_query(query, fetch="all", to_df_columns=columns_to_insert)
    df.replace({np.nan: None, pd.NaT: None}, inplace=True)
    return df


def update_drive_table_data(df_database, df_to_update, column_to_insert):
    for index, row in df_to_update.iterrows():
        changes = {}
        for col in column_to_insert:
            if col not in ("key", "updated", "action", "changes") and str(row[col]) != str(df_database.loc[df_database["key"] == row["key"], col].values[0]):
                changes[col] = {
                    "old": str(df_database.loc[df_database["key"] == row["key"], col].values[0]),
                    "new": str(row[col])
                }

        if changes:
            row["action"] = "update"
            row["changes"] = json.dumps(changes)

        if row["status"] == 1:
            row["action"] = "delete"

        query = f"""
            UPDATE {Constants.DB_SCHEMA_NAME}.{Constants.DRIVE_TABLE_NAME}
            SET {', '.join([f"{col} = %s" for col in column_to_insert if col != 'key'])}
            WHERE key = %s
        """
        params = tuple(row[col] for col in column_to_insert if col != 'key') + (row['key'],)
        try:
            run_query(query, params, fetch="none")
        except Exception as e:
            logger.error(f"Error updating row {row['key']}: {e}")
            raise DatabaseException("Error updating SA tank data. Please connect with dev team.")


def insert_drive_table_data(df_to_insert, columns_to_insert):
    for index, row in df_to_insert.iterrows():
        if row["status"] == 1:
            row["action"] = "delete"

        query = f"""
            INSERT INTO {Constants.DB_SCHEMA_NAME}.{Constants.DRIVE_TABLE_NAME}
            ({', '.join(columns_to_insert)})
            VALUES({', '.join(['%s'] * len(columns_to_insert))})
        """
        params = tuple(row[col] for col in columns_to_insert)
        try:
            run_query(query, params, fetch="none")
            logger.info(f"Inserted row {index} - {row['key']}")
        except Exception as e:
            logger.error(f"Error inserting row {row['key']}: {e}")
            raise DatabaseException("Error inserting SA tank data. Please connect with dev team.")
        

def insert_data_log_api(data):
    query = f"""
        INSERT INTO {Constants.DB_SCHEMA_NAME}.{Constants.LOG_TABLE_NAME}
        (drive_name, file_name, status, progress, error_report, environment, created_timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        data['drive_name'],
        data['file_name'],
        data['status'],
        data['progress'],
        json.dumps(data['error_report']),
        data['environment'],
        data['created_timestamp']
    )
    run_query(query, params, fetch="none")