from http.client import responses
from response_builder import ResponseBuilder
from constants import Constants

class GenericException(Exception):
    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.message = error_message

    def generate_response(self):
        response = self.__dict__.copy()
        response.pop("status_code")
        return ResponseBuilder(self.status_code, response).generate_response()
    
class BadRequestexception(GenericException):
    def __init__(self, error_message):
        GenericException.__init__(self, 400, error_message)

class NotFoundException(GenericException):
    def __init__(self, error_message):
        GenericException.__init__(self, 404, error_message)