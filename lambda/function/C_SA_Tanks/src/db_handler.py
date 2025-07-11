from constants import Constants
from datetime import datetime
from database import Database
import pandas as pd
import numpy as np
import json
from custom_exception import BadRequestException

def get_column_template():
    query = f"""
    SELECT drive_column_name FROM {Constants.DB_SCHEMA_NAME}.{Constants.DRIVE_TEMPLATE_TABLE_NAME} WHERE drive_name = '{Constants.DRIVE_NAME}'"""
    try:
        db = Database()
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                db.release_connection(conn)
                return result           
    except Exception as e:
        raise BadRequestException(f"Error fetching column templates: {e}") from e
 

def load_drive_template():
    query = f"""
    INSERT INTO {Constants.DB_SCHEMA_NAME}.{Constants.DRIVE_TEMPLATE_TABLE_NAME}
    (drive_name, drive_type, drive_column_name, created_by, created_timestamp, updated_timestamp, version)
    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id"""
    try:
        db = Database()
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (
                    Constants.DRIVE_NAME,
                    "",
                    json.dumps(Constants.COLUMNS_TEMPLATE),
                    "KUMRAK2",
                    datetime.now(),
                    datetime.now(),
                    "v1"
                ))
                inserted_id = cursor.fetchone()[0]
                conn.commit()
                db.release_connection(conn)
                return inserted_id
    except Exception as e:
        raise BadRequestException(f"Error loading drive template: {e}") from e

def get_existing_file_name():
    query = f"""
    SELECT file_name FROM {Constants.DB_SCHEMA_NAME}.{Constants.DRIVE_TEMPLATE_TABLE_NAME}
    """
    try:
        db = Database()
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                db.release_connection(conn)
                return pd.DataFrame(result, columns=['file_name'])
    except Exception as e:
        raise BadRequestException(f"Error fetching existing file name: {e}") from e

def load_drive_content(file_name, file_path):
    query = f"""
    INSERT INTO {Constants.DB_SCHEMA_NAME}.{Constants.DRIVE_CONTENT_TABLE_NAME}
    (drive_type, file_name, s3_path, uploaded_by, result_log_path, created_timestamp, delete_timestamp, is_deleted, version)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"""
    try:
        db = Database()
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (
                    "",
                    file_name,
                    file_path,
                    "KUMRAK2",
                    "None",
                    datetime.now(),
                    None,
                    False,
                    "v1"
                ))
                inserted_id = cursor.fetchone()[0]
                conn.commit()
                db.release_connection(conn)
                return inserted_id
    except Exception as e:
        raise BadRequestException(f"Error loading drive content: {e}") from e

def get_sa_tank_data(columns_to_insert):
    query = f"""
    SELECT {str(', '.join(columns_to_insert))} FROM {Constants.DB_SCHEMA_NAME}.{Constants.DRIVE_TABLE_NAME}
    """
    try:
        db = Database()
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                db.release_connection(conn)
                df_database = pd.DataFrame(result, columns=columns_to_insert)
                df_database.replace({np.nan: None, pd.NaT: None}, inplace=True)
                return df_database
    except Exception as e:
        raise BadRequestException(f"Error fetching SA tank data: {e}") from e

def update_sa_tank_data(df_database, df_to_update, column_to_insert):
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
        try:
            db = Database()
            with db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, tuple(row[col] for col in column_to_insert if col != 'key') + (row['key'],))
                    conn.commit()
                    db.release_connection(conn)
        except Exception as e:
            print(f"Error updating row: {e}, {row['key']}")
            raise BadRequestException(f"Error updating SA tank data: {e}") from e

def insert_sa_tank_data(df_to_insert, columns_to_insert):
    for index, row in df_to_insert.iterrows():
        if row["status"] == 1:
            row["action"] = "delete"

        query = f"""
        INSERT INTO {Constants.DB_SCHEMA_NAME}.{Constants.DRIVE_TABLE_NAME}
        ({', '.join(columns_to_insert)})
        VALUES({', '.join(['%s'] * len(columns_to_insert))})
        """
        try:
            db = Database()
            with db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, tuple(row[col] for col in columns_to_insert))
                    conn.commit()
                    print("inserted in database: ", index, row['key'])
                    db.release_connection(conn)
        except Exception as e:
            print(f"Error inserting row: {e}, {row['key']}")
            raise BadRequestException(f"Error inserting SA tank data: {e}") from e

def insert_data_log_api(data):
    query = f"""
    INSERT INTO {Constants.DB_SCHEMA_NAME}.{Constants.LOG_TABLE_NAME}
    (drive_name, file_name, status, progress, error_report, environment, created_timestamp)
    VALUES(%s, %s, %s, %s, %s, %s, %s)
    """

    data['error_report'] = json.dumps(data['error_report'])

    values = (
        data['drive_name'],
        data['file_name'],
        data['status'],
        data['progress'],
        data['error_report'],
        data['environment'],
        data['created_timestamp']
    )
    try:
        db = Database()
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
                db.release_connection(conn)
    except Exception as e:
        raise BadRequestException(f"Error inserting data log table: {e}") from e
   
        



