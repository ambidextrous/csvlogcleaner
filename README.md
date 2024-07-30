# CSV Log Cleaner

## What is this?

`csvlogcleaner` - Cleans [Comma Separated Value (CSV)](https://en.wikipedia.org/wiki/Comma-separated_values) files to conform to a given type schema by parallelized streaming through configurably-sized memory buffers, with column-wise logging of any resulting data loss. Prepares unvalidated data in CSV tables for use in databases or data pipelines. Processes arbitrarily large files in memory-constrained environments.

The Python `csvlogcleaner` library is a Python wrapper around the [CSV Log Cleaner](https://github.com/ambidextrous/csv_log_cleaner) library implemented in Rust, which is also available as a Rust crate or a stand-alone Command Line Interface (CLI) via [Cargo](https://crates.io/crates/csv_log_cleaner).

## Example useage

Installation:
```bash
pip install csvlogcleaner
```

Useage:
```python
(rust) aidanbutler@ADH120-MBP csvlogcleaner % python
Python 3.12.0 (main, Feb 28 2024, 11:31:25) [Clang 14.0.3 (clang-1403.0.22.14.1)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from csvlogcleaner import clean_csv
>>> from io import StringIO
>>> from tempfile import NamedTemporaryFile
>>> import json
>>> schema = {'columns': [{'name': 'INT_COLUMN', 'column_type': 'Int'}, {'name': 'STRING_COLUMN', 'column_type': 'String', 'nullable': False}, {'name': 'DATE_COLUMN', 'column_type': 'Date', 'format': '%Y-%m-%d'}, {'name': 'ENUM_COLUMN', 'column_type': 'Enum', 'nullable': False, 'legal_vals': ['V1', 'V2', 'V3'], 'illegal_val_replacement': 'V1'}]}
>>> input = '''INT_COLUMN,STRING_COLUMN,DATE_COLUMN,ENUM_COLUMN\n4,dog,2020-12-31,V1\nnot_an_int,cat,not_a_date,V2\n
an_int,weasel,a_date,V5\n'''
>>> print(input)
INT_COLUMN,STRING_COLUMN,DATE_COLUMN,ENUM_COLUMN
4,dog,2020-12-31,V1
not_an_int,cat,not_a_date,V2
an_int,weasel,a_date,V5
>>> with NamedTemporaryFile() as f:
...     with open(f.name, "w") as file:
...         file.write(input)
...     result_json = clean_csv(f.name, "TEST_OUTPUT", json.dumps(schema), 1000)
...     print(json.loads(result_json))
...     with open("TEST_OUTPUT", "r") as file2:
...         print(str(file2.read()))
... 
122
{'total_rows': 3, 'log_map': {'DATE_COLUMN': {'name': 'DATE_COLUMN', 'invalid_count': 2, 'max_invalid': 'not_a_date', 'min_invalid': 'a_date'}, 'ENUM_COLUMN': {'name': 'ENUM_COLUMN', 'invalid_count': 1, 'max_invalid': 'V5', 'min_invalid': 'V5'}, 'STRING_COLUMN': {'name': 'STRING_COLUMN', 'invalid_count': 0, 'max_invalid': None, 'min_invalid': None}, 'INT_COLUMN': {'name': 'INT_COLUMN', 'invalid_count': 2, 'max_invalid': 'not_an_int', 'min_invalid': 'an_int'}}}
INT_COLUMN,STRING_COLUMN,DATE_COLUMN,ENUM_COLUMN
4,dog,2020-12-31,V1
,cat,,V2
,weasel,,V1
```

See `tests` directory for further example usage.

## Description

The `csvlogcleaner` library takes a JSON CSV schema definition (e.g. one defining a `NAME` column of type String, an `AGE` column of type Int and a `DATE_OF_BIRTH` column of type Date) and a `CSV` file which is required to conform to that definition and cleans the input data to conform with the schema definition.

Illegal values are either cleaned (e.g. by adding `.0` to the end of integer values in a float column) or deleted (e.g. by replacing a `not_a_float` string value in a float column with an empty string), with all data loss being logged in an output JSON file, along with the maximum and minimum illegal values encountered.

Data is processed row-wise, in adjustably-sized buffers using all of the available cores for parallel processing. The aim here is to make it possible to process larger-than-memory datasets quickly and efficiently, as part of an extendable Unix pipeline.

### Parameters
The library exposes the following Python function to users:
```python
clean_csv(input_csv_path: str, output_csv_path: str, schema_string: str, buffer_size: int=1000) -> str:
```
Parameter explanation:
- `input_csv_path` - _required_ path to input CSV file.
- `output_csv_path` - _required_ path to output CSV file.
- `schema` - _required_ can be either the path to a JSON schema file with a name of the form `*.json` or an in-line JSON-string definition, e.g. `'{"columns": [{"name": "INT_COLUMN","column_type": "Int"},{"name": "STRING_COLUMN","column_type": "String","nullable": false}]}'`
- `buffer_size` - _optional_ buffer size integer (default  `1000`) indicating the number of rows to be held in each buffer of rows allocated a new thread for processing. The programme uses all available threads, so if there are 10 cores available, and the buffer value is set to 1,000, then up to 10,000 rows will be held in buffers at any one time during processing.
Return value:
- A JSON string indicating the level of data loss during the cleansing process, if any. Of the form: `{'total_rows': 3, 'log_map': {'DATE_COLUMN': {'name': 'DATE_COLUMN', 'invalid_count': 2, 'max_invalid': 'not_a_date', 'min_invalid': 'a_date'}, 'ENUM_COLUMN': {'name': 'ENUM_COLUMN', 'invalid_count': 1, 'max_invalid': 'V5', 'min_invalid': 'V5'}, 'STRING_COLUMN': {'name': 'STRING_COLUMN', 'invalid_count': 0, 'max_invalid': None, 'min_invalid': None}, 'INT_COLUMN': {'name': 'INT_COLUMN', 'invalid_count': 2, 'max_invalid': 'not_an_int', 'min_invalid': 'an_int'}}}`

### Source 

Source code for this Python library can be found on GitHub, [here](https://github.com/ambidextrous/csvlogcleaner). PR-requests to make improvements, add missing functionality or fix bugs are all very welcome; as is opening of GitHub issues to request fixes or features.

## Why?

The simplicity of the CSV format means that the data such files contain is by its nature un-typed. A valid CSV will give the user no guarantees that the contents of the fields it contains are anything other than strings. This - combined with the fact that CSV files are often generated by error-prone, manual processes - presents a problem when it comes to processing CSV data in ways that require columns to have a particular type. For example, one cannot safely set up a data pipeline to sum the contents of an `AMOUNT_PAID` column when there is no guarantee that it will not contain string values like `"not_a_float"`.

There are multiple existing solutions to this problem, each of which involve their own limitations. 

One solution is what could be lablelled as "Total Permissiveness". This is the default strategy used, for example, by Python's `pandas` dataframe processing library. This approach means that if a single illegal `12.34\n` float value is found in a column, the entire column will read as a string column. This approach keeps the reading logic simple, but means that the processing logic has to be more complex: as you have to write your code with no guarantees that an `AMOUNT_PAID` column will actually contain numerical values.

A second is what could be labelled as "Total Strictness". This is the default strategy used, for example, by the PostgreSQL relational database. This approach means a type schema for the CSV data is used, and that if - for example - a single illegal `12.34\n` float value is found in a column, the entire CSV reading operation will fail. This approach means that it is possible to keep both the writing and processing code simple, but means that reads are often likely to fail when faced with large datasets containing even a tiny proportion of illegal values.

To overcome the limitations of Total Permissiveness and Total Strictness, a third approach is sometimes used, which could be labelled as "Silent Coercion". This approach means a type schema for the CSV data is used, and that if - for example - a single illegal `12.34\n` float value is found in a column, that value will be silently replaced with a NULL value. This approach means that it is possible to keep both the writing and processing code simple, but means insidous data loss can go undetected. For example, this approach could result in an entire `DATE_OF_BIRTH` field being silently replaced with `NULL` values because the dates were formatted as `YYYY-DD-MM` instead of the expected `YYYY-MM-DD` format.

The aim of `csv_log_cleaner` is to enable data processors to make use of an approach that could be labelled as "Coercion with Data Loss Logging". In this approach, the user provides a type schema definition for their CSV data and the tool will guarantee that the data piped through the tool will conform that schema (e.g. by removing the illegal trailing `\n` from the end of a `12.34\n` value in a float column, or by deleting entirely a `not_a_valid_float` value from the same column) and logging both the number of deleted values in each column and the maximum and minimum illegal values encountered. This means that users can be confident that their pipeline will not fail due to input type errors either on read or during processing. In addition, any data loss that does take place during the cleaning operation will be logged in a human and computer readable JSON log file - including sample maximum and mimumn illegal values found and illegal value counts and proportions - which can be used to monitor data loss. For example, a monitoring script could be used to ignore data loss in a particular columm if it is below a given threshold value (e.g. 1%) and to raise an alert otherwise.

## Limitations

- Only supports UTF-8-encoded input data (consider using [`iconv`](https://linux.die.net/man/1/iconv) or similar tools to convert non-UTF-8 data to the required encoding as part of a pipeline)
- Row output order will generally not match row output order, due to individual rows being processed separately across multiple threads.
- Uses empty string values as NULLs across all column types (meaning that other recognised NULL values - such as `<NA>` and `null` - will be converted to empty strings in output, and that all empty string values will be treated as NULL)


## Schema Definition

The type schema must be a JSON file or string, of the form:
```json
{
    "columns": [
        {
            "name": "INT_COLUMN",
            "column_type": "Int", 
        },
        {
            "name": "STRING_COLUMN",
            "column_type": "String",
            "nullable": false
        },
        {
            "name": "DATE_COLUMN",
            "column_type": "Date",
            "format": "%Y-%m-%d"
        },
        {
            "name": "ENUM_COLUMN",
            "column_type": "Enum",
            "nullable": false,
            "legal_vals": ["V1", "V2", "V3"],
            "illegal_val_replacement": "V1"
        }
    ]
}
```

Column attribute explanation:
* "name": _required_ - must correspond with name of column in CSV file
* "column_type": _required_ - must be one of "String", "Int", "Date", "Float", "Enum" or "Bool"
* "nullable": _optional_ - default value is `true`
* "legal_vals": _required for Enum type columns_ - list of accepted string values
* "illegal_val_replacement": _optional for Enum type columns_ - default value is empty string
* "format": _required for Date type columns_ - should match the syntax described [here](https://docs.rs/chrono/latest/chrono/format/strftime/index.html)

## Null handling

* The following list of values in the input CSV file are interpretted as `NULL`s by the tool: `["", "#N/A","#N/A N/A","#NA","-1.#IND","-1.#QNAN","-NaN","-nan","1.#IND","1.#QNAN","<NA>","N/A","NA","NULL","NaN","n/a","nan","null"]`

## Building from source

Requires a working Rust [Cargo](https://doc.rust-lang.org/cargo/) installation, a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html) running at least Python version 3.8 and a [maturin](https://github.com/PyO3/maturin) installation.
```bash
pip install maturin
git clone https://github.com/ambidextrous/csvlogcleaner.git
cd csvlogcleaner
maturin develop
```
You should then be able to run the above example code starting:
```bash
python # To start the Python shell 
>>> from csvlogcleaner import clean_csv # to import csvlogcleaner within the shell
```
