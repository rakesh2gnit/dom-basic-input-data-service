import os

class Constants:
    # Database Configuration
    DB_SCHMEMA_NAME = os.environ.get("DB_SCHEMA")
    DB_NAME = os.getenv("dbname")
    USERNAME = os.getenv("DB_USERNAME")
    HOST = os.getenv("DB_HOST", "localhost")
    PORT = os.getenv("DB_PORT", "5432") 

    # AWS Configuration
    DB_SECRET_NAME = os.getenv("secret_name")
    AWS_REGION = os.getenv("region")

    # Database Table Names
    TABLE_NAME = "basic_data_hu_marketvarianten"

    # Datadog Configuration
    DATADOG_SERVICE_NAME = "dom-basic-input-data-service"
    DATADOG_FUNCTION_NAME = "N_HU_marketvarianten_RDS_API"

    #General Timestamp
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%fZ"