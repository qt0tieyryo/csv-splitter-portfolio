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

## Tools and scoped services

- **Use this splitter for free:** the code and synthetic examples in this repository
  are MIT-licensed. A [free browser CSV audit](https://csv.gaodea.top/) runs locally.
- **For repeat batch work:** the optional
  [CSV Rescue Batch Kit](https://nianjun.gumroad.com/l/brupq) adds an offline browser
  workbench, batch auditing/cleanup, CSV-to-JSON export, examples and documentation.
  It is currently listed at US$9.99; check the product page for the final price and
  requirements. The MIT splitter remains available here at no charge.
- **Discuss a custom task:** see the [service scopes and original web demo](https://csv.gaodea.top/services.html),
  or email [support@gaodea.top](mailto:support@gaodea.top) with a redacted example,
  expected output, budget and deadline. Data preparation, small static websites and
  narrowly scoped web fixes are considered after scope and payment checks. An
  enquiry is not an accepted order or a delivery commitment.

- **Caption videos and supplied-source briefs:** see the [original AI-assisted samples](https://csv.gaodea.top/ai-services.html), including a 29.82-second caption video using synthetic CSV identifiers and a project-fact brief. Indicative pilot quotes are US$20 for the defined caption-video scope and from US$30 for a supplied-source brief. Final scope, rights, acceptance checks and a supported funded order must be agreed first.

The workflow uses AI assistance and tested scripts. All public samples are
synthetic; no customer results, testimonials or revenue claims are implied.
Do not send confidential source files, credentials, identity or payment details.
