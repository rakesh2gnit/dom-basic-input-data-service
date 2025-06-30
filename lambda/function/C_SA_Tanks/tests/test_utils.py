from unittest import mock
from src.utils import get_secret_dict
import json

def test_get_secret_dict():
    with mock.patch('boto3.session.Session') as mock_session:
        mock_client = mock.Mock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': json.dumps({'key': 'value'})
        }
        
        secret_name = "test_secret"
        result = get_secret_dict(secret_name)
        
        assert result['SecretString'] == json.dumps({'key': 'value'})
        