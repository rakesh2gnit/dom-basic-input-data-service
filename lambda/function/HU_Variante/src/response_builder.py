import json

class ResponseBuilder:
    def __init__(self, status_code, response):
        self.status_code = status_code
        self.response = response
        #self.headers = {
        #    "Access-Control-Allow-Origin":"*",
        #    "Access-Control-Allow-Methods":"POST, OPTIONS",
        #    "Access-Control-Allow-Headers":"*",
        #}
        
    def generate_response(self):
        return{
            'statusCode': self.status_code,
            'body': json.dumps(self.response)
        }
        #'headers': self.headers