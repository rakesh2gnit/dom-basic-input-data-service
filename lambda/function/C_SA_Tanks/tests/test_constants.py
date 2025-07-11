import pytest
from src.constants import Constants
import os

def test_column_template():
    # Test if the column template is a dictionary
    expected_template = {
        "Verkaufsbezeichnung":"sales_name",
        "Baumuster":"baumuster",
        "Getriebeart":"gear_type",
        "Verbrennungsmotor":"internal_combustion_engine",
    }
    assert Constants.COLUMNS_TEMPLATE == expected_template


def test_drive_table_name():
    assert Constants.DRIVE_TABLE_NAME == "basic-data_c_sa_tanks"

def test_db_schema_name():
    # Test if the DB schema name is set correctly
    assert Constants.DB_SCHEMA_NAME == os.environ.get("DB_SCHEMA")