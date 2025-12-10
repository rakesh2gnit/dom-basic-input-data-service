import json
import os
from datetime import datetime

import numpy as np
import pandas as pd

from database import Database
from constants import Constants
from log import logger as base_logger
import utils


logger = base_logger(
    service_name=Constants.DATADOG_SERVICE_NAME,
    lambda_function_name=Constants.DATADOG_FUNCTION_NAME,
)


def lambda_handler(event, context):
    # ---------- CORS ----------
    headers = event.get("headers", {}) or {}
    origin = headers.get("origin", "")
    allowed_origins = [
        o.strip() for o in os.getenv("ALLOWED_ORIGIN", "").split(",") if o.strip()
    ]
    allow_origin = None

    if origin in allowed_origins:
        allow_origin = origin
    elif allowed_origins:
        allow_origin = allowed_origins[0]

    # ---------- Filters ----------
    filters = event.get("queryStringParameters", {}) or {}

    if not filters:
        return build_response(
            400,
            {
                "message": (
                    "At least one parameter is required. "
                    "Eg. page=1 or col_name=col_value in the parameter."
                )
            },
            allow_origin,
        )

    try:
        (
            total_records,
            total_pages,
            invalid_page,
            json_records,
            last_modified_date,
        ) = get_data_from_table(filters)

        logger.info(
            f"total_records: {total_records}, "
            f"total_pages: {total_pages}, "
            f"records_count: {len(json_records)}"
        )

        if invalid_page:
            return build_response(
                400,
                {
                    "message": (
                        "The requested page exceeds the total number of pages available. "
                        f"Valid page range is between 1 to {total_pages}."
                    )
                },
                allow_origin,
            )
        elif total_records == 0:
            return build_response(
                200,
                {"message": "No records found."},
                allow_origin,
            )

        data = {
            "totalRecords": total_records,
            "totalPages": total_pages,
            "last_modified_date": last_modified_date,
            "data": json_records,
        }
        return build_response(200, data, allow_origin, use_decimal_encoder=True)

    except Exception as e:
        # Detailed error handling
        if isinstance(e, ValueError):
            logger.error(f"ValueError: {e}")
            return build_response(400, {"message": "Invalid Timestamp Format!"}, allow_origin)
        elif isinstance(e, KeyError):
            logger.error(f"KeyError: {e}")
            return build_response(400, {"message": f"Missing required filter: {e}"}, allow_origin)
        elif isinstance(e, TypeError):
            logger.error(f"TypeError: {e}")
            return build_response(400, {"message": "Invalid filter value type"}, allow_origin)
        else:
            logger.error(f"Unhandled Exception: {e}")
            return build_response(500, {"message": "Internal server error"}, allow_origin)


def get_data_from_table(filters: dict):
    try:
        page = int(filters.get("page", 1))         # Default page is 1
        limit = int(filters.get("pageSize", 25))   # Default page size is 25
        last_modified = filters.get("last_modified", "false").lower() == "true"

        # Calculate OFFSET based on page
        offset = (page - 1) * limit

        where_clause = []
        params = []
        vehicle_filter_clause = ""
        vehicle_filter_params = []

        for key, value in filters.items():
            # Skip pagination and control params
            if key in ["page", "pageSize", "last_modified"]:
                continue

            # Handle multiple values (comma-separated string)
            if "," in value:
                value_list = [v.strip() for v in value.split(",") if v.strip()]

                if key == "vehicle_name":
                    placeholders = ", ".join(["%s"] * len(value_list))
                    vehicle_filter_clause = (f"WHERE vehicle_name IN ({placeholders})")
                    vehicle_filter_params.extend(value_list)
                    
                if key in ["created", "updated"]:
                    try:
                        parsed_values = [
                            datetime.strptime(v, Constants.TIMESTAMP_FORMAT).strftime(
                                "%Y-%m-%d %H:%M"
                            )
                            for v in value_list
                        ]
                    except ValueError:
                        raise ValueError(f"Invalid timestamp format for '{key}': {value}")

                    column_expr = f"TO_CHAR({key}, 'YYYY-MM-DD HH24:MI')"
                    placeholders = ", ".join(["%s"] * len(parsed_values))
                    where_clause.append(f"{column_expr} IN ({placeholders})")
                    params.extend(parsed_values)
                else:
                    # Case-insensitive filtering, optional special handling
                    if key in ["sales_term_german"]:
                        # Single value, normalized lower
                        normalized_values = [value.strip().lower()]
                    else:
                        normalized_values = [v.lower() for v in value_list]

                    column_expr = f"LOWER({key})"
                    placeholders = ", ".join(["%s"] * len(normalized_values))
                    where_clause.append(f"{column_expr} IN ({placeholders})")
                    params.extend(normalized_values)

            # Single value
            else:
                value = value.strip()
                if key == "vehicle_name":
                    vehicle_filter_clause = f"WHERE vehicle_name = %s"
                    vehicle_filter_params.append(value)

                if key in ["created", "updated"]:
                    try:
                        dt = datetime.strptime(value, Constants.TIMESTAMP_FORMAT)
                    except ValueError:
                        raise ValueError(f"Invalid timestamp format for '{key}': {value}")

                    where_clause.append(
                        f"TO_CHAR({key}, 'YYYY-MM-DD HH24:MI') = %s"
                    )
                    params.append(dt.strftime("%Y-%m-%d %H:%M"))

                else:
                    # Remove whitespace and compare case-insensitive
                    # IMPORTANT: escape backslash properly to avoid invalid escape sequence warnings
                    where_clause.append(
                        "regexp_replace(LOWER({col}), '\\s+', '', 'g') = "
                        "regexp_replace(LOWER(%s), '\\s+', '', 'g')".format(col=key)
                    )
                    params.append(value.lower())

        if last_modified:
            where_clause.append("action IN ('update')")

        # Build base query
        base_query = f"FROM {Constants.DB_SCHEMA_NAME}.{Constants.DRIVE_TABLE_NAME}"
        if where_clause:
            base_query += " WHERE " + " AND ".join(where_clause)

        logger.info(f"Base query: {base_query}")
        logger.info(f"Query params: {params}")

        # Distinct vehicle count (per distinct market_code + vehicle_name)
        vehicle_count_query = (
            f"FROM ("
            f"  SELECT DISTINCT market_code, vehicle_name "
            f"  FROM {Constants.DB_SCHEMA_NAME}.basic_data_l_ausstattungsliste"
            f"  {vehicle_filter_clause}"
            f") t"
        )

        total_vehicle_count = get_total_records(vehicle_count_query, vehicle_filter_params)
        logger.info(f"total_vehicle_count = {total_vehicle_count}")

        total_base_records = get_total_records(base_query, params)
        logger.info(f"raw total_records (without division) = {total_base_records}")

        if total_vehicle_count > 0:
            total_records = total_base_records // total_vehicle_count
        else:
            total_records = 0

        logger.info(f"total_records (per vehicle) = {total_records}")
        logger.info(f"limit (pageSize) = {limit}")

        total_pages = (total_records + limit - 1) // limit if total_records else 0
        logger.info(f"total_pages = {total_pages}")

        invalid_page = page > total_pages and total_pages > 0

        # Adjust LIMIT to account for vehicle count
        effective_limit = limit * max(total_vehicle_count, 1)
        logger.info(f"final effective limit = {effective_limit}")

        full_query = (
            f"SELECT * {base_query} "
            f"ORDER BY updated DESC "
            f"LIMIT %s OFFSET %s"
        )
        params_with_paging = params + [effective_limit, offset]

        logger.info(f"Final SQL Query: {full_query}")
        logger.info(f"Query params with paging: {params_with_paging}")

        rows, colnames = fetch_filtered_records(full_query, params_with_paging)

        # ---------- DataFrame handling ----------
        df = pd.DataFrame(rows, columns=colnames)
        df.replace({np.nan: None, pd.NaT: None}, inplace=True)

        # Drop unnecessary columns
        df.drop(columns=["id", "key", "additional_data"], errors="ignore", inplace=True)

        if not df.empty:
            # Combine vehicle_name and baumuster
            if "vehicle_name" in df.columns and "baumuster" in df.columns:
                df["vehicle_name"] = (
                    df["vehicle_name"].astype(str)
                    + " ("
                    + df["baumuster"].astype(str)
                    + ")"
                )
                df.drop(columns=["baumuster"], errors="ignore", inplace=True)

            last_modified_date = df["updated"].max() if "updated" in df.columns else None
        else:
            last_modified_date = None

        # Convert DataFrame to list of dicts
        json_records = df.to_dict(orient="records")

        return total_records, total_pages, invalid_page, json_records, last_modified_date

    except Exception as error:
        if isinstance(error, ValueError):
            logger.error(f"ValueError in get_data_from_table: {error}")
        elif isinstance(error, KeyError):
            logger.error(f"KeyError in get_data_from_table: {error}")
        elif isinstance(error, TypeError):
            logger.error(f"TypeError in get_data_from_table: {error}")
        else:
            logger.error(f"Error fetching data from table: {error}")
        raise


def get_total_records(base_query: str, params=None) -> int:
    """
    Execute: SELECT COUNT(*) {base_query}
    base_query should start with FROM ...
    """
    if params is None:
        params = []

    query = f"SELECT COUNT(*) {base_query}"
    db = Database()
    connection = None

    try:
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        logger.error(f"Error in fetching total records: {e}")
        raise
    finally:
        if connection is not None:
            db.release_connection(connection)


def fetch_filtered_records(query: str, params: list):
    db = Database()
    connection = None

    try:
        connection = db.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]
            return rows, colnames
    except Exception as e:
        logger.error(f"Error in fetching filtered records: {e}")
        raise
    finally:
        if connection is not None:
            db.release_connection(connection)


def build_response(status_code, body_dict, allow_origin, use_decimal_encoder=False):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": allow_origin or "",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "X-XSS-Protection": "1; mode=block",
        "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy": "default-src 'self'",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "X-Download-Options": "noopen",
        "X-Permitted-Cross-Domain-Policies": "none",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    }

    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(
            body_dict,
            indent=4,
            cls=utils.DecimalEncoder if use_decimal_encoder else None,
        ),
    }
