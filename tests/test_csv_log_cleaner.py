from tempfile import NamedTemporaryFile
import json

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

    # Act
    with NamedTemporaryFile() as temp_file:
        result_raw = clean_csv(input_csv_path, temp_file.name, input_schema_path, 1000)
        print(result_raw)
        result = json.loads(result_raw)
        print(result)

        # Assert
        assert result == expected_result


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

    # Act
    with NamedTemporaryFile() as temp_file:
        result_raw = clean_csv(input_csv_path, temp_file.name, json.dumps(input_schema), 1000)
        print(result_raw)
        result = json.loads(result_raw)
        print(result)

        # Assert
        assert result == expected_result
