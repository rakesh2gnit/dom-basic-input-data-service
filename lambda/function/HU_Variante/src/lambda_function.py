from dataclasses import asdict
from constants import Constants
from extraction_logic import extraction_data
from response_builder import ResponseBuilder
from custom_exception import *
from urllib.parse import unquote_plus

import os
import utils

def save_into_database(s3Filename, dataframe):
    table = utils.dynamodb_table()
    report_obj = utils.create_report_body(s3Filename, dataframe)
    table.put_item(Item=asdict(report_obj))
    return report_obj

def lambda_handler(event, context):
    file_name = event['Records'][0]['s3']['object']['key']
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    s3filename = unquote_plus(os.path.basename(file_name))

    print(bucket_name)
    print(s3filename)

    try:
        dataframe = extraction_data(Constants.bucketName, Constants.pkwHBerichte+"/"+s3filename)
        report_obj = save_into_database(s3filename, dataframe)
        response = utils.generate_success_response(report_obj)
        return response
    
    except GenericException as e:
        report_obj = save_into_database(s3filename, None)
        response = utils.generate_fail_response(report_obj)
        return response