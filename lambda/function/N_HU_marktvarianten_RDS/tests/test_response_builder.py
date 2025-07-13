import pytest
from src.response_builder import ResponseBuilder
import json

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

def test_generate_response_json_error():
    # JSON can't serialize a function
    unserializable = {"bad": test_generate_response_json_error}

    builder = ResponseBuilder(200, unserializable)
    result = builder.generate_response()

    assert result["statusCode"] == 500
    assert "Internal Server Error" in json.loads(result["body"])["error"]

