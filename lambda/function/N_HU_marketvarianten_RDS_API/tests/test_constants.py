import os

class Constants:
    # Database Configuration
    DB_SCHMEMA_NAME = os.environ.get("DB_SCHEMA")
    DB_NAME = os.getenv("dbname")
    USERNAME = os.getenv("DB_USERNAME", "default_user")
    HOST = os.getenv("DB_HOST", "localhost")
    PORT = os.getenv("DB_PORT", "5432") 

    # AWS Configuration
    DB_SECRET_NAME = os.getenv("secret_name")
    AWS_REGION = os.getenv("region")