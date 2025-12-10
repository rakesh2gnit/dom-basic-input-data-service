from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging.formatters.datadog import DatadogLogFormatter

#Generic Function to create the Logger
def logger(service_name, lambda_function_name):
    return Logger(
        service=service_name,
        logger_formatter=DatadogLogFormatter(),
        lambda_function_name=lambda_function_name
    )

    