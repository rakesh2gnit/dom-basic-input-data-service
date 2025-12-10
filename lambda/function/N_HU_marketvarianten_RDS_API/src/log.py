from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging.formatters.datadog import DatadogLogFormatter

# Generic function to create the logger
def logger(service_name, lambda_function_name):
    return Logger(
        service=service_name,
        logger_formatter=DatadogLogFormatter(),
        lambda_function_name=lambda_function_name
    )