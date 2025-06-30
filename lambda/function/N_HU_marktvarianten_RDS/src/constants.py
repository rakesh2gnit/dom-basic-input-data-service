import os

class Constants:
    # Drive name
    DRIVE_NAME = "N_HU_Marktvarianten"

    # Development Environment
    ENVIRONMENT = "DEV"

    # Database Configuration
    DB_SCHEMA_NAME = os.environ.get("DB_SCHEMA")
    DRIVE_TEMPLATE_TABLE_NAME = "basic_data_drive_template"
    DRIVE_CONTENT_TABLE_NAME = "basic_data_drive_contents"
    DRIVE_TABLE_NAME = "basic_data_hu_marketvariant"
    SUB_DRIVE_TABLE_NAME = "basic_data_hu_variant"
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

    #Success Message
    SUCCESS_ESSAGE_FILE_PROCESS = "- file has been proccessed successfully "
    FAILED_MESSAGE_FILE_PROCESS = "- file has been failed "

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