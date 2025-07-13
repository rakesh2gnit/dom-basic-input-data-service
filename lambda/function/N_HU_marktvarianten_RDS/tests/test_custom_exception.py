import pytest

from src.custom_exception import BadRequestException, NotFoundException, DatabaseException, AWSSecretException, EmptyDataException, ColumnValidationException, RowValidationException
import json

@pytest.mark.parametrize("exception_cls, expected_status", [
    (BadRequestException, 400),
    (NotFoundException, 404),
    (DatabaseException, 502),
    (AWSSecretException, 504),
    (EmptyDataException, 402),
    (ColumnValidationException, 422),
    (RowValidationException, 422),
])

def test_generate_response_structure(exception_cls, expected_status):
    error_message = "Something went wrong"
    exc = exception_cls(error_message)

    response = exc.generate_response()

    assert response["statusCode"] == expected_status
    assert "body" in response

    # Parse and check the body content
    body = json.loads(response["body"])
    assert body["message"] == error_message