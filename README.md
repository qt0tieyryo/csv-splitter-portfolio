# CSV splitter portfolio

A small original Python service demonstration for splitting a UTF-8 CSV by record
count. It preserves decoded string values, quoted commas, multiline fields,
Unicode and leading zeros, repeats the header and writes a count/SHA-256 report.
It streams rows, does not upload data and refuses an existing destination folder.

## Run

Python 3.10 or later, standard library only:

```sh
python split_csv.py synthetic.csv your-new-output --rows-per-part 5
python -m unittest -v test_split_csv.py
```

The included synthetic example has 12 records. The demo output contains 5, 5 and 2
records; reconstructing the parts was verified to match every original cell string.
The five tests cover preservation, existing-file safety, malformed/ragged input,
source changes during processing, empty/header-only files and split-size validation.
These are software checks and synthetic examples, not past customer orders.

## Limits

UTF-8/UTF-8 BOM and one header row. Rejects inconsistent field counts. Output
quoting/newlines are canonical CSV; source byte formatting is not preserved.
No type inference, cleanup or spreadsheet formula escaping. Import identifier
columns as Text and do not execute untrusted spreadsheet formulas. Existing
zeros that were already lost cannot be reconstructed. No production claim for
arbitrary file sizes or encodings.

Original code, AI-assisted development. MIT license. Free browser audit:
https://csv.gaodea.top/ . No customer data or credentials are included.
