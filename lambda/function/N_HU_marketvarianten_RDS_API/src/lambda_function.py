import json
import os
import pandas as pd
import numpy as np
import utils
from database import Database
from constants import Constants
from log import logger
from datetime import datetime, timezone

logger = logger(service_name=Constants.DATADOG_SERVICE_NAME, lambda_function_name=Constants.DATADOG_FUNCTION_NAME)

def lambda_handler(event, context):
    headers = event.get('headers', {})
    origin = headers.get('origin', '')
    allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
    allow_origin = origin if origin in allowed_origins else (allowed_origins[0] if allowed_origins else None)

    filters = event.get('queryStringParameters', {})
    if not filters:
        return build_response(400, {'message': 'At least one filter is required'}, allow_origin)

    try:
        total_records, total_pages, invalid_page, json_records, last_modified_data = get_n_hu_marketvarianten(filters)

        if invalid_page:
            return build_response(400, {'message': f"Invalid page number {total_pages}"}, allow_origin)
        elif total_records == 0:
            return build_response(200, {'message': 'No records found'}, allow_origin)

        data = {
            "total_records": total_records,
            "total_pages": total_pages,
            "last_modified_data": last_modified_data,
            "data": json_records
        }
        return build_response(200, data, allow_origin, use_decimal_encoder=True)

    except Exception as e:
        if isinstance(e, ValueError):
            logger.error(f"ValueError: {e}")
            return build_response(400, {'message': str(e)}, allow_origin)
        elif isinstance(e, KeyError):
            logger.error(f"KeyError: {e}")
            return build_response(400, {'message': f"Missing required filter: {e}"}, allow_origin)
        elif isinstance(e, TypeError):
            logger.error(f"TypeError: {e}")
            return build_response(400, {'message': 'Invalid filter value type'}, allow_origin)
        else:
            logger.error(f"Error processing request: {e}")
            return build_response(500, {'message': 'Internal server error'}, allow_origin)


def get_n_hu_marketvarianten(filters):
    try:
        page = int(filters.get('page', 1))
        limit = int(filters.get('pageSize', 100))
        last_modified = filters.get('last_modified', 'false').lower() == 'true'

        offset = (page - 1) * limit

        where_clause = []
        params = []

        for key, value in filters.items():
            if key in ['page', 'pageSize', 'last_modified']:
                continue

            if ',' in value:
                value_list = value.split(',')
                if key in ['created', 'updated']:
                    # Parse and truncate all datetime values to minute precision
                    try:
                        parsed_values = [datetime.strptime(v.strip(), Constants.TIMESTAMP_FORMAT).strftime('%Y-%m-%d %H:%M') for v in value_list]
                    except ValueError:
                        raise ValueError(f"Invalid timestamp format for '{key}': {value}")
                    column_expr = f"TO_CHAR({key}, 'YYYY-MM-DD HH24:MI')"
                    placeholders = ', '.join(['%s'] * len(parsed_values))
                    where_clause.append(f"{column_expr} IN ({placeholders})")
                    params.extend(parsed_values)
                else:
                    value_list = [v.strip().lower() for v in value_list]
                    column_expr = f"LOWER({key})"
                    placeholders = ', '.join(['%s'] * len(value_list))
                    where_clause.append(f"{column_expr} IN ({placeholders})")
                    params.extend(value_list)
            else:
                if key in ['created', 'updated']:
                    try:
                        dt = datetime.strptime(value, Constants.TIMESTAMP_FORMAT)
                    except ValueError:
                        raise ValueError(f"Invalid timestamp format for '{key}': {value}")
                    where_clause.append(f"TO_CHAR({key}, 'YYYY-MM-DD HH24:MI') = %s")
                    params.append(dt.strftime('%Y-%m-%d %H:%M'))
                else:
                    where_clause.append(f"LOWER({key}) = LOWER(%s)")
                    params.append(value.lower())

        if last_modified:
            where_clause.append("action IN ('insert', 'update', 'delete')")

        base_query = f"FROM {Constants.DB_SCHMEMA_NAME}.{Constants.TABLE_NAME}"
        if where_clause:
            base_query += " WHERE " + " AND ".join(where_clause)

        total_records = get_total_records(base_query, params)
        total_pages = (total_records + limit - 1) // limit if total_records else 0
        invalid_page = page > total_pages and total_pages > 0

        full_query = f"SELECT * {base_query} ORDER BY updated DESC LIMIT %s OFFSET %s"
        params_with_paging = params + [limit, offset]
        logger.info(f"Final SQL query: {full_query}")
        logger.info(f"Query params: {params_with_paging}")

        rows, colnames = fetch_filtered_records(full_query, params_with_paging)

        df = pd.DataFrame(rows, columns=colnames)
        df.replace({np.nan: None, pd.NaT: None}, inplace=True)
        df.drop(columns=['id', 'key', 'additinal_data'], errors='ignore', inplace=True)

        last_modified_data = df['updated'].max() if not df.empty else None
        json_records = df.to_dict(orient='records')

        return total_records, total_pages, invalid_page, json_records, last_modified_data
    except Exception as e:
        if isinstance(e, ValueError):
            logger.error(f"ValueError in get_n_hu_marketvarianten: {e}")
        elif isinstance(e, KeyError):
            logger.error(f"KeyError in get_n_hu_marketvarianten: {e}")
        elif isinstance(e, TypeError):
            logger.error(f"TypeError in get_n_hu_marketvarianten: {e}")
        else:
            logger.error(f"Error in get_n_hu_marketvarianten: {e}")
        raise


def get_total_records(base_query, params):
    query = f"SELECT COUNT(*) {base_query}"
    db = Database()
    try:
        with db.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Error in get_total_records: {e}")
        raise
    finally:
        db.release_connection(connection)


def fetch_filtered_records(query, params):
    db = Database()
    try:
        with db.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                colnames = [desc[0] for desc in cursor.description]
                return rows, colnames
    except Exception as e:
        logger.error(f"Error in fetch_filtered_records: {e}")
        raise
    finally:
        db.release_connection(connection)


def build_response(status_code, body_dict, allow_origin, use_decimal_encoder=False):
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': allow_origin,
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'X-XSS-Protection': '1; mode=block',
        'X-Content-Type-Options': 'nosniff'
    }

    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(body_dict, indent=4, cls=utils.DecimalEncoder if use_decimal_encoder else None)
    }
