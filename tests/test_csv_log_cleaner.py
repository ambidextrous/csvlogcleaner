from tempfile import NamedTemporaryFile
import json
import os

from csvlogcleaner import clean_csv


def test_clean_csv_schema_file():
    # Arrange
    input_csv_path = "tests/test_data/test_input.csv"
    input_schema_path = "tests/test_data/test_schema.json"

    expected_result = {
        "total_rows": 3,
        "log_map": {
            "INT_COLUMN": {
                "name": "INT_COLUMN",
                "invalid_count": 2,
                "max_invalid": "not_an_int",
                "min_invalid": "an_int",
            },
            "DATE_COLUMN": {
                "name": "DATE_COLUMN",
                "invalid_count": 2,
                "max_invalid": "not_a_date",
                "min_invalid": "a_date",
            },
            "STRING_COLUMN": {
                "name": "STRING_COLUMN",
                "invalid_count": 0,
                "max_invalid": None,
                "min_invalid": None,
            },
            "ENUM_COLUMN": {
                "name": "ENUM_COLUMN",
                "invalid_count": 1,
                "max_invalid": "V5",
                "min_invalid": "V5",
            },
        },
    }
    expected_csv_output = """INT_COLUMN,STRING_COLUMN,DATE_COLUMN,ENUM_COLUMN
4,dog,2020-12-31,V1
,cat,,V2
,weasel,,V1\n"""

    # Act
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name

    try:
        result_raw = clean_csv(input_csv_path, temp_file_path, input_schema_path, 1000)
        print(result_raw)
        result = json.loads(result_raw)
        print(result)
        with open(temp_file_path) as f:
            cleaned_csv_output = f.read()
            print(cleaned_csv_output)

            # Assert
            assert result == expected_result
            assert cleaned_csv_output == expected_csv_output
    finally:
        os.remove(temp_file_path)


def test_clean_csv_schema_string():
    # Arrange
    input_csv_path = "tests/test_data/test_input.csv"

    input_schema = {
        "columns": [
            {"name": "INT_COLUMN", "column_type": "Int"},
            {"name": "STRING_COLUMN", "column_type": "String", "nullable": False},
            {"name": "DATE_COLUMN", "column_type": "Date", "format": "%Y-%m-%d"},
            {
                "name": "ENUM_COLUMN",
                "column_type": "Enum",
                "nullable": False,
                "legal_vals": ["V1", "V2", "V3"],
                "illegal_val_replacement": "V1",
            },
        ]
    }

    expected_result = {
        "total_rows": 3,
        "log_map": {
            "INT_COLUMN": {
                "name": "INT_COLUMN",
                "invalid_count": 2,
                "max_invalid": "not_an_int",
                "min_invalid": "an_int",
            },
            "DATE_COLUMN": {
                "name": "DATE_COLUMN",
                "invalid_count": 2,
                "max_invalid": "not_a_date",
                "min_invalid": "a_date",
            },
            "STRING_COLUMN": {
                "name": "STRING_COLUMN",
                "invalid_count": 0,
                "max_invalid": None,
                "min_invalid": None,
            },
            "ENUM_COLUMN": {
                "name": "ENUM_COLUMN",
                "invalid_count": 1,
                "max_invalid": "V5",
                "min_invalid": "V5",
            },
        },
    }
    expected_csv_output = """INT_COLUMN,STRING_COLUMN,DATE_COLUMN,ENUM_COLUMN
4,dog,2020-12-31,V1
,cat,,V2
,weasel,,V1\n"""

    # Act
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name

    try:
        result_raw = clean_csv(input_csv_path, temp_file_path, json.dumps(input_schema))
        print(result_raw)
        result = json.loads(result_raw)
        print(result)
        with open(temp_file_path) as f:
            cleaned_csv_output = f.read()
            print(cleaned_csv_output)

            # Assert
            assert result == expected_result
            assert cleaned_csv_output == expected_csv_output
    finally:
        os.remove(temp_file_path)