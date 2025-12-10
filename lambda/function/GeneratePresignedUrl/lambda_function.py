import json
import os
import base64
import traceback

import boto3
import botocore
from botocore.exceptions import NoCredentialsError

import utils
import data_validation
from custom_exception import EmptyDataException

logger = utils.logger(
    service_name="basic-data-service",
    lambda_function_name="generate-presigned-url-api-service"
)

# Reuse S3 client across invocations (better performance)
s3_client = boto3.client("s3")

ALLOWED_OPERATIONS = {"upload", "download"}
MAX_DRIVE_DATA_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
DEFAULT_PRESIGNED_EXPIRATION = 600  # seconds


def generate_presigned_url(bucket_name, object_name, operation, expiration=DEFAULT_PRESIGNED_EXPIRATION, metadata=None):
    """
    Generate a presigned URL for S3 upload/download.
    """
    try:
        if operation == "upload":
            params = {"Bucket": bucket_name, "Key": object_name}
            if metadata:
                params["Metadata"] = metadata
            response = s3_client.generate_presigned_url(
                "put_object", Params=params, ExpiresIn=expiration
            )
        elif operation == "download":
            response = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": object_name},
                ExpiresIn=expiration,
            )
        else:
            logger.warning(f"Unknown operation requested: {operation}")
            return None
    except NoCredentialsError:
        logger.error("AWS credentials not found")
        return None
    except Exception as error:
        logger.error(f"Error generating presigned URL: {error}")
        return None

    return response


def parse_metadata(metadata):
    """
    Parse and validate base64-encoded JSON metadata under key 'drive_data'.
    Returns the decoded body dict.
    """
    # If metadata comes as JSON string, parse it
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
        except json.JSONDecodeError as error:
            logger.error(f"Metadata is not valid JSON: {error}")
            raise ValueError("Invalid metadata JSON")

    logger.debug(f"metadata: {metadata}")

    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a JSON object")

    base64_data = metadata.get("drive_data")
    if base64_data is None:
        raise KeyError("Missing 'drive_data' in metadata")

    # Limit payload size (approx 4/3 of original base64)
    if len(base64_data) > (MAX_DRIVE_DATA_SIZE_BYTES * 4 // 3):
        logger.error("Payload too large")
        raise ValueError("Payload too large")

    try:
        decoded_bytes = base64.b64decode(base64_data)
    except base64.binascii.Error as error:
        logger.error(f"Base64 decode error: {error}")
        raise ValueError("Invalid base64 encoding")

    try:
        decoded_string = decoded_bytes.decode("utf-8")
    except UnicodeDecodeError:
        decoded_string = decoded_bytes.decode("latin1")

    try:
        body = json.loads(decoded_string)
    except json.JSONDecodeError as error:
        logger.error(f"JSON decode error: {error}")
        raise ValueError("Invalid JSON in drive_data")

    data_validation.check_empty_data(body, "body payload missing!")
    return body


def get_drive_from(metadata_body):
    drive_name = metadata_body.get("drive_name")
    data_validation.check_empty_data(drive_name, "Missing Drive name!")
    return drive_name


def validate_upload_body(body):
    file_name = body.get("file_name")
    file_path = body.get("file_path")
    uploaded_by = body.get("uploaded_by")

    data_validation.check_empty_data(file_name, "Missing file name!")
    data_validation.check_empty_data(file_path, "Missing file path!")
    data_validation.check_empty_data(uploaded_by, "Missing upload user name!")


def file_exists(bucket, key):
    """
    Check if file exists in S3 bucket.
    """
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "404":
            return False
        logger.error(f"Error checking file existence: {e}")
        raise


def handle_upload(origin, bucket_name, body):
    are_files_exist = body.get("are_files_exist", False)
    uploads = body.get("uploads", [])

    # Basic validation
    if not isinstance(uploads, list) or not uploads:
        data = {"Error": "Missing or invalid 'uploads' list"}
        return utils.response_builder(origin, 400, data)

    # Case 1: only check if files exist
    if are_files_exist:
        files = []
        for item in uploads:
            object_name = item.get("object_name")
            if not object_name:
                continue
            try:
                if file_exists(bucket_name, object_name):
                    files.append(object_name)
            except Exception:
                # If head_object fails for reasons other than 404, we log and continue
                logger.exception(f"Error checking file existence for {object_name}")

        data = {"files_list": files}
        return utils.response_builder(origin, 200, data)

    # Case 2: generate upload URLs
    try:
        url_list = []
        for item in uploads:
            object_name = item.get("object_name")
            if not object_name:
                raise KeyError("Missing 'object_name' in uploads item")

            metadata_raw = item.get("metadata", {})
            metadata_body = parse_metadata(metadata_raw)
            logger.debug(f"metadata_body: {metadata_body}")

            # Validate drive name & required fields for upload
            drive_name = get_drive_from(metadata_body)
            logger.debug(f"drive_name: {drive_name}")

            validate_upload_body(metadata_body)

            logger.info(f"Generating upload URL: bucket={bucket_name}, key={object_name}")
            url = generate_presigned_url(
                bucket_name=bucket_name,
                object_name=object_name,
                operation="upload",
                expiration=DEFAULT_PRESIGNED_EXPIRATION,
                metadata=metadata_raw if isinstance(metadata_raw, dict) else None,
            )

            if not url:
                data = {"Error": "Error generating presigned URL"}
                return utils.response_builder(origin, 400, data)

            url_list.append({"object_name": object_name, "url": url})

    except (KeyError, ValueError, EmptyDataException) as error:
        logger.error(f"Validation/Parsing error: {error}\n{traceback.format_exc()}")
        return utils.response_builder(origin, 400, {"Error": str(error)})
    except Exception as error:
        logger.error(f"Unexpected error: {error}\n{traceback.format_exc()}")
        return utils.response_builder(origin, 500, {"Error": "Internal server error"})

    data = {"urls": url_list}
    return utils.response_builder(origin, 200, data)


def handle_download(origin, bucket_name, body):
    """
    Handle download operation for a single object.
    Expected body: {"operation": "download", "object_name": "<key>"}
    """
    object_name = body.get("object_name")
    if not object_name:
        data = {"Error": "Missing 'object_name' for download"}
        return utils.response_builder(origin, 400, data)

    logger.info(f"Generating download URL: bucket={bucket_name}, key={object_name}")
    url = generate_presigned_url(
        bucket_name=bucket_name,
        object_name=object_name,
        operation="download",
        expiration=DEFAULT_PRESIGNED_EXPIRATION,
    )

    if not url:
        data = {"Error": "Error generating presigned URL"}
        return utils.response_builder(origin, 400, data)

    data = {"url": url}
    return utils.response_builder(origin, 200, data)


def lambda_handler(event, context):
    logger.info("Lambda invoked")

    bucket_name = os.getenv("BUCKET_NAME", "")
    headers = event.get("headers", {}) or {}
    origin = headers.get("origin", "")

    # Parse body safely
    raw_body = event.get("body")
    if raw_body is None:
        data = {"Error": "Missing request body"}
        return utils.response_builder(origin, 400, data)

    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError:
        data = {"Error": "Invalid JSON in request body"}
        return utils.response_builder(origin, 400, data)

    if not isinstance(body, dict) or not body:
        data = {"Error": "Missing required parameters"}
        return utils.response_builder(origin, 400, data)

    operation = body.get("operation", "").lower()
    if operation not in ALLOWED_OPERATIONS:
        data = {"Error": "Operation not allowed"}
        return utils.response_builder(origin, 400, data)

    # Branch by operation
    if operation == "upload":
        return handle_upload(origin, bucket_name, body)
    else:  # download
        return handle_download(origin, bucket_name, body)
