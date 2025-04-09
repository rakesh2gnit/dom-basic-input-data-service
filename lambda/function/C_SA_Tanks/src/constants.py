import os

class Constants:
    COLUMNS_TEMPLATE = {
        "Verkaufsbezeichnung":"sales_name",
        "Baumuster":"baumuster",
        "Getriebeart":"gear_type",
        "Verbrennungsmotor":"internal_combustion_engine",
    }

    DRIVE_TABLE_NAME = "basic-data_c_sa_tanks"

    DB_SCHEMA_NAME = os.environ.get("DB_SCHEMA")

    AWS_REGION = os.environ.get("region_name")

    TEAMS_WEBHOOK_SECRET_NAME = os.environ.get("teams-webook-secret-name")

    DB_SECRET_NAME = os.getenv("secret_name")

    LOG_TABLE_NAME = "basic_data_logs"

    DRIVE_TEMPLATE_TABLE_NAME = "basic-data_drive_templates"

    DRIVE_CONTENT_TABLE_NAME = "basic-data_drive_contents"

    DRIVE_NAME = "C_SA_Tanks"

    ENVIRONMENT = "DEV"

    PROCESS_DONE = "seccessed"

    SUCCESS_PROGRESS = "100%"

    SUCCESS_MESSAGE = "file has been processed successfully"

    PROCESS_FAILED = "failed"

    ERROR_PROGRESS = "0%"

    FAILED_MESSAGE = "file has been failed"

    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%fZ"

    DATADOG_SERVICE_NAME = "basic-data-service"

    DATADOG_FUNCTION_NAME = "c-sa-tanks-service"
    
