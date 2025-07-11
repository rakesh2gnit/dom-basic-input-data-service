import json

class ResponseBuilder:
    def __init__(self, status_code, response):
        self.status_code = status_code
        self.response = response

    def generate_response(self):
        try:
            return {
                'statusCode': self.status_code,
                'body': json.dumps(self.response)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Internal Server Error',
                    'message': str(e)
                })
            }