import boto3
from requests import session
from constants import Constants
from botocore.exceptions import ClientError
from custom_exception import InternalServerException
from decimal import Decimal
from datetime import datetime, date
import json

def get_secret_dict(secret_name):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=Constants.AWS_REGION)
    
    try:
        get_secret_value = client.get_secret_value(SecretId=secret_name)
        return get_secret_value
    except ClientError as e:
        print(f"Error retrieving secret {secret_name}: {e}")
        raise InternalServerException(f"Error retrieving secret {secret_name}: {e}")

#Custom JSON encoder to handle Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj) # or str(obj) if you prefer
        if isinstance(obj, datetime) or isinstance(obj, date):
            return str(obj) # or str(obj) if you prefer
        return super(DecimalEncoder, self).default(obj)