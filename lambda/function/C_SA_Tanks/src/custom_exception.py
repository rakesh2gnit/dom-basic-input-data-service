from response_builder import ResponseBuilder

class GenericException(Exception):
    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.error_message = error_message

    def generate_response(self):
        response = self.__dict__.copy()
        response.pop('status_code')
        return ResponseBuilder(self.status_code, response).generate_response()
    
class DatabaseException(GenericException):
    def __init__(self, error_message):
        GenericException.__init__(self, 502, error_message)

class BadRequestException(GenericException):
    def __init__(self, error_message):
        GenericException.__init__(self, 400, error_message)

class InternalServerException(GenericException):
    def __init__(self, error_message):
        GenericException.__init__(self, 500, error_message)

class AWSCredException(GenericException):
    def __init__(self, error_message):
        GenericException.__init__(self, 504, error_message)

