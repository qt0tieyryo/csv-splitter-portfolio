"""Split UTF-8 CSV by record count, preserving decoded string values.

No pandas, type inference, uploads, source changes, or existing output replacement.
Output uses canonical UTF-8 CSV quoting/newlines; it is not byte-identical to input.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def split_csv(source, destination, rows_per_part=500000):
    source, destination = Path(source).resolve(), Path(destination).absolute()
    if rows_per_part < 1:
        raise ValueError('rows_per_part must be positive')
    if destination.exists():
        raise FileExistsError('Use a new output directory; existing data will not be replaced')
    if not source.is_file():
        raise FileNotFoundError(source)
    source_hash = sha256(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    parts, total, target = [], 0, None
    # Keep staging on the same filesystem so final rename is atomic.
    with tempfile.TemporaryDirectory(prefix='.csv-split-', dir=destination.parent) as staging:
        staging = Path(staging)
        try:
            with source.open('r', encoding='utf-8-sig', newline='') as input_stream:
                reader = csv.reader(input_stream, strict=True)
                try:
                    header = next(reader)
                except StopIteration:
                    raise ValueError('CSV is empty') from None
                if not header:
                    raise ValueError('CSV must have a header row')
                for record_index, row in enumerate(reader, start=2):
                    if len(row) != len(header):
                        raise ValueError(f'Record {record_index}: expected {len(header)} fields, got {len(row)}')
                    if total % rows_per_part == 0:
                        if target is not None:
                            target.close()
                        name = f'part-{len(parts) + 1:04d}.csv'
                        target = (staging / name).open('w', encoding='utf-8', newline='')
                        writer = csv.writer(target)
                        writer.writerow(header)
                        parts.append({'file': name, 'data_records': 0})
                    writer.writerow(row)
                    parts[-1]['data_records'] += 1
                    total += 1
            if target is not None:
                target.close()
                target = None
            if not parts:  # Header-only source still produces a usable header-only output.
                with (staging / 'part-0001.csv').open('w', encoding='utf-8', newline='') as output:
                    csv.writer(output).writerow(header)
                parts.append({'file': 'part-0001.csv', 'data_records': 0})
            if sha256(source) != source_hash:
                raise ValueError('Source changed during processing; no output published')
            for part in parts:
                part['sha256'] = sha256(staging / part['file'])
            report = {'schema_version': 1, 'source_sha256': source_hash,
                      'encoding': 'UTF-8', 'data_records': total, 'columns': len(header),
                      'rows_per_part': rows_per_part, 'parts': parts,
                      'preservation': 'Decoded strings preserved; no type inference or formula escaping',
                      'spreadsheet_note': 'Import identifier columns as Text. Do not open untrusted formulas.'}
            (staging / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
            if destination.exists():
                raise FileExistsError('Output directory appeared during processing')
            os.rename(staging, destination)
            return report
        finally:
            if target is not None:
                target.close()


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--rows-per-part', type=int, default=500000)
    args = parser.parse_args()
    try:
        print(json.dumps(split_csv(args.source, args.destination, args.rows_per_part), indent=2))
    except (OSError, ValueError, csv.Error, UnicodeError) as error:
        print(f'Cannot split CSV: {error}', file=sys.stderr)
        raise SystemExit(1)
