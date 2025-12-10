import os

class Constants:

    DRIVE_NAME = "L_Ausstattungslisten"

    DRIVE_TABLE_NAME = "basic_data_l_ausstattungslisten"

    DB_SCHEMA_NAME = os.environ.get("DB_SCHEMA")

    DB_NAME = os.environ.get("dbname")

    USERNAME = os.environ.get("username")

    HOST= os.environ.get("host")

    PORT = os.environ.get("port")

    AWS_REGION = os.environ.get("region")

    DB_SECRET_NAME = os.environ.get("secret_name")

    DATADOG_SERVICE_NAME = "basic-data-service"

    DATADOG_FUNCTION_NAME = "1-ausstattungslisten-api-service"

    TIMESTAMP_FORMAT= "%Y-%m-%d %H:%M:%S.%f"