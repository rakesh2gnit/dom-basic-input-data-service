from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging.formatters.datadog import DatadogLogFormatter
import json
import os

# Generic Function to create the Logger
def logger(service_name, lambda_function_name):
    return Logger(service=service_name, logger_formatter=DatadogLogFormatter(), lambda_function_name=lambda_function_name)

def response_builder(origin, status_code, data):
    allowed_origins = [o for o in os.getenv("ALLOWED_ORIGIN", "").split(",") if o.strip()]

    if origin in allowed_origins:
        allow_origin = origin
    elif allowed_origins:
        allow_origin = allowed_origins[0]
    else:
        # No allowed origins configured, do not set Access-Control-Allow-Origin
        allow_origin = None

    headers = {
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, Content-Encoding",
        "X-XSS-Protection": "1; mode=block",
        "X-Content-Type-Options": "nosniff"
    }

    if allow_origin:
        headers["Access-Control-Allow-Origin"] = allow_origin

    response = {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(data)
    }

    return response