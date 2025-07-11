import os

class Constants:

    #Column name
    COLUMNS_TEMPLATE = {
                    "BR" : "br",
                    "AA" : "aa",
                    "AJ/MOPF" : "aj_mopf",
                    "AJ/MOPF-Paket" : "aj_paket",
                    "Paaket PU-Termin" : "paket_pu_termin",
                    "Paketname" : "paketname",
                    "Paket-Projektleiter" : "paket_projektleiter",
                    "Bemerkung" : "bemerkung",
                    "Paket-Status" : "paket_status"
                    }
    
    # Drive name
    DRIVE_NAME = "N_HU_Marktvarianten"

    # Development Environment
    ENVIRONMENT = os.environ.get("ENVIRONMENT")

    # Database Configuration
    DB_SCHEMA_NAME = os.environ.get("DB_SCHEMA")
    DB_NAME = os.environ.get("dbname")
    USERNAME = os.environ.get("username")
    HOST = os.environ.get("host")
    PORT = os.environ.get("port", "5432")

    # Table Names
    DRIVE_TEMPLATE_TABLE_NAME = "basic_data_drive_template"
    DRIVE_CONTENT_TABLE_NAME = "basic_data_drive_contents"
    DRIVE_TABLE_NAME = "basic_data_hu_marketvariant"
    SUB_TABLE_NAME = "basic_data_hu_variant"
    LOG_TABLE_NAME = "basic_data_logs"

    # AWS Configuration
    DB_SECRET_NAME = os.environ.get("secret_name")
    AWS_REGION = os.environ.get("region")
    TEAMS_WEBHOOK_SECRET_NAME = os.environ.get("teams_webhook_secret_name")

    # Datadog Configuration
    DATADOG_SERVICE_NAME = "basic-data-service"
    DATADOG_FUNCTION_NAME = "n-hu-marketvariant-service"

    #General Timestamp
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%fZ"

    #Process Status
    PROCESS_DONE = "successed"
    PROCESS_FAILED = "failed"

    # Progress Status
    SUCCESS_PROGRESS = "100%"
    ERROR_PROGRESS = "0%"

    # Messages
    SUCCESS_MESSAGE = "- file has been proccessed successfully."
    FAILED_MESSAGE = "- file has been failed."
    ERROR_MESSAGE = "Something went wrong while processing the file. Please contact support team."
    EMPTY_DATA_MESSAGE = "The uploaded file has no data."   