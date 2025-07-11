import pytest
from src.response_builder import ResponseBuilder

def test_generate_success_response():
    response = {"message": "Success"}
    builder = ResponseBuilder(200, response)
    result = builder.generate_response()

    assert result["statusCode"] == 200
    assert result["body"] == '{"message": "Success"}'

def test_generate_error_response():
    response = {"error": "Internal Server Error"}
    builder = ResponseBuilder(500, response)
    result = builder.generate_response()

    assert result["statusCode"] == 500
    assert result["body"] == '{"error": "Internal Server Error"}'
