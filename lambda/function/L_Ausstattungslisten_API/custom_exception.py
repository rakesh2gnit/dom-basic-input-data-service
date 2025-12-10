from response_builder import ResponseBuilder

#Define a custom exception class for generating responses
class GenericException (Exception):
    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.message = error_message

    def generate_response(self):
        response = self.__dict__.copy()
        response.pop("status_code")
        return ResponseBuilder(self.status_code, response).generate_response()

#Subclass for BadRequestException
class BadRequestException (GenericException):
    def __init__(self, error_message):
        GenericException.__init__(self, 400, error_message)

# Subclass for file validation
class InvalidFileException (GenericException):
    def __init__(self, error_message):
        GenericException.__init__(self, 401, error_message)

#Subclass for empty data validation
class EmptyDataException(GenericException):
    def __init__(self, error_message):
        GenericException.__init__(self, 402, error_message)

#Subclass to check columns validation
class ColumnValidationException (GenericException):
    def __init__(self, error_message):
        GenericException.__init__(self, 422, error_message)

# Subclass to check rows validation
class RowValidationException(GenericException):
    def __init__(self, error_message):
        GenericException.__init__(self, 422, error_message)

#Subclass for InternalServerException
class InternalServerException (GenericException):
    def __init__(self, error_message):
        GenericException.__init__(self, 500, error_message)

# Subclass for database exception
class DatabaseException (GenericException):
    def __init__(self, error_message):
        GenericException.__init__(self, 502, error_message)

# Subclass for AWS exception
class AWSCredException (GenericException):
    def __init__(self, error_message):
        GenericException.__init__(self, 504, error_message)