import boto3
import json
from datetime import datetime
from constants import Constants
from models import Report
from response_builder import ResponseBuilder

import os
import requests

def dynamodb_table():
    dynamodb = boto3.resource(Constants.dynamodb_resource)
    table = dynamodb.Table(Constants.basic_data_h_berichte_table_name)
    return table

def get_current_timestamp():
    current_time = datetime.utcnow()
    timestamp_str = current_time.strftime(Constants.timestamp_format)[:-3]
    return timestamp_str

def create_report_body(filename, dataframe):
    current_timestamp = get_current_timestamp()
    data_list = []
    process_status = Constants.process_failed

    if dataframe is not None and not dataframe.empty:
        process_status = Constants.process_done
        data_list = json.loads(dataframe.to_json(orient='records'))

    report_obj = Report(
        report_key=Constants.report_type,
        report_file_name=filename,
        created_timestamp=current_timestamp,
        updated_timestamp=current_timestamp,
        data=data_list,
        status=process_status
    )
    return report_obj

def generate_success_response(report_obj):
    message = report_obj.report_file_name+" - "+Constants.success_message_file_process+report_obj.status
    response = ResponseBuilder(status_code=200, response={'message':message, 'file_name':report_obj.report_file_name})
    return response.generate_response()

def generate_fail_response(report_obj):
    message = report_obj.report_file_name+" - "+Constants.success_message_file_process+report_obj.status
    response = ResponseBuilder(status_code=403, response={'message':message, 'file_name':report_obj.report_file_name})
    return response.generate_response()

