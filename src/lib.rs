use csv::{Reader, Writer};
use csv_log_cleaner::{clean_csv as clean_csv_rust, get_schema_from_json_str, Column};
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use std::collections::HashMap;
use std::fs;

#[pyfunction]
#[pyo3(signature = (input_csv_path, output_csv_path, schema_string, buffer_size=1000))]
fn clean_csv(
    input_csv_path: String,
    output_csv_path: String,
    schema_string: String,
    buffer_size: usize,
) -> PyResult<String> {
    let schema_map: HashMap<String, Column> = if std::path::Path::new(&schema_string)
        .extension()
        .map_or(false, |ext| ext.eq_ignore_ascii_case("json"))
    {
        let schema_file_contents = fs::read_to_string(schema_string)?;
        get_schema_from_json_str(&schema_file_contents)?
    } else {
        get_schema_from_json_str(&schema_string)?
    };

    let mut csv_rdr = Reader::from_path(input_csv_path)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let csv_wtr = Writer::from_path(output_csv_path)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;

    let result = clean_csv_rust(&mut csv_rdr, csv_wtr, schema_map, buffer_size);

    match result {
        Ok(log) => {
            let log_str = serde_json::to_string(&log)
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
            Ok(log_str)
        }
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
    }
}

#[pymodule]
fn csvlogcleaner(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(clean_csv, m)?)?;
    Ok(())
}
