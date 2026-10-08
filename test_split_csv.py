import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from split_csv import split_csv, sha256


class SplitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source.csv'

    def write(self, rows):
        with self.source.open('w', encoding='utf-8-sig', newline='') as stream:
            csv.writer(stream).writerows(rows)

    def test_preserves_strings_quoted_newlines_and_source(self):
        rows = [['id', 'note', 'amount'], ['00127', 'line one\nline two', '000.00'],
                ['00008', 'comma, quote " preserved', '=1+1'], ['00999', '中文', '1e10']]
        self.write(rows)
        before = self.source.read_bytes()
        destination = self.root / 'parts'
        report = split_csv(self.source, destination, 2)
        self.assertEqual([p['data_records'] for p in report['parts']], [2, 1])
        reconstructed = []
        for part in report['parts']:
            with (destination / part['file']).open(encoding='utf-8', newline='') as stream:
                content = list(csv.reader(stream))
            self.assertEqual(content[0], rows[0])
            reconstructed.extend(content[1:])
            self.assertEqual(part['sha256'], sha256(destination / part['file']))
        self.assertEqual(reconstructed, rows[1:])
        self.assertEqual(before, self.source.read_bytes())
        self.assertEqual(json.loads((destination / 'report.json').read_text())['data_records'], 3)

    def test_existing_destination_is_untouched(self):
        self.write([['id'], ['001']])
        destination = self.root / 'parts'
        destination.mkdir()
        marker = destination / 'important.txt'
        marker.write_text('keep')
        with self.assertRaises(FileExistsError):
            split_csv(self.source, destination)
        self.assertEqual(marker.read_text(), 'keep')

    def test_ragged_and_malformed_input_publish_nothing(self):
        for content in ['a,b\n1\n', 'a,b\n1,"unterminated\n']:
            self.source.write_text(content, encoding='utf-8')
            destination = self.root / 'parts'
            with self.assertRaises((ValueError, csv.Error)):
                split_csv(self.source, destination)
            self.assertFalse(destination.exists())
            self.assertFalse(list(self.root.glob('.csv-split-*')))

    def test_changed_source_publish_nothing(self):
        self.write([['id'], ['001']])
        destination = self.root / 'parts'
        with patch('split_csv.sha256', side_effect=['original', 'changed']):
            with self.assertRaisesRegex(ValueError, 'Source changed'):
                split_csv(self.source, destination)
        self.assertFalse(destination.exists())

    def test_empty_header_only_and_invalid_size(self):
        self.source.write_text('', encoding='utf-8')
        with self.assertRaises(ValueError):
            split_csv(self.source, self.root / 'parts')
        self.write([['id']])
        report = split_csv(self.source, self.root / 'parts')
        self.assertEqual(report['data_records'], 0)
        self.assertEqual(len(report['parts']), 1)
        with self.assertRaises(ValueError):
            split_csv(self.source, self.root / 'other', 0)


if __name__ == '__main__':
    unittest.main()
