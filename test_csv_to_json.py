import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import csv_to_json as converter


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.source = Path(self.directory.name) / "source.csv"
        self.output = Path(self.directory.name) / "result.json"

    def write_source(self, text):
        self.source.write_text(text, encoding="utf-8")

    def test_bom_unicode_and_string_values(self):
        self.write_source('\ufeffid,name,amount,active\n0007,Мила,12.50,true\n0008,Zoë,,false\n')
        self.assertEqual(converter.convert(self.source, self.output), 2)
        self.assertEqual(json.loads(self.output.read_text(encoding="utf-8")), [
            {"id": "0007", "name": "Мила", "amount": "12.50", "active": "true"},
            {"id": "0008", "name": "Zoë", "amount": "", "active": "false"},
        ])

    def test_delimiter_quoted_separator_and_multiline_field(self):
        self.write_source('id;note\n01;"hello; there\nsecond line"\n')
        converter.convert(self.source, self.output, delimiter=";")
        self.assertEqual(json.loads(self.output.read_text()), [
            {"id": "01", "note": "hello; there\nsecond line"}
        ])

    def test_bad_headers_and_cell_counts_leave_no_output(self):
        cases = [
            ("", "header row"),
            ("a,\n1,2\n", "empty"),
            ("a,   \n1,2\n", "empty"),
            ("a,a\n1,2\n", "unique"),
            ("a,b\n1,2\n3\n", "expected 2 cells, found 1"),
            ("a,b\n1,2,3\n", "expected 2 cells, found 3"),
            ("a,b\n\n", "expected 2 cells, found 0"),
        ]
        for text, error in cases:
            with self.subTest(text=text):
                self.write_source(text)
                with self.assertRaisesRegex(converter.ConversionError, error):
                    converter.convert(self.source, self.output)
                self.assertFalse(self.output.exists())

    def test_unclosed_quote_is_rejected(self):
        self.write_source('a,b\n1,"unfinished\n')
        with self.assertRaisesRegex(converter.ConversionError, "invalid CSV"):
            converter.convert(self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_invalid_utf8_is_rejected(self):
        self.source.write_bytes(b"name\n\xff\n")
        with self.assertRaises(UnicodeDecodeError):
            converter.convert(self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_existing_output_is_preserved(self):
        self.write_source("id\n001\n")
        self.output.write_text("original")
        with self.assertRaisesRegex(converter.ConversionError, "already exists"):
            converter.convert(self.source, self.output)
        self.assertEqual(self.output.read_text(), "original")

    def test_output_created_during_conversion_is_preserved(self):
        self.write_source("id\n001\n")
        original_read = converter.read_records

        def read_and_create_output(*args):
            records = original_read(*args)
            self.output.write_text("concurrent output")
            return records

        with patch.object(converter, "read_records", side_effect=read_and_create_output):
            with self.assertRaisesRegex(converter.ConversionError, "already exists"):
                converter.convert(self.source, self.output)
        self.assertEqual(self.output.read_text(), "concurrent output")
        self.assertEqual(list(self.output.parent.glob(".csv-json-*.tmp")), [])

    def test_overwrite_requires_valid_input(self):
        self.output.write_text("original")
        self.write_source("a,b\n1\n")
        with self.assertRaises(converter.ConversionError):
            converter.convert(self.source, self.output, overwrite=True)
        self.assertEqual(self.output.read_text(), "original")
        self.write_source("id\n001\n")
        converter.convert(self.source, self.output, overwrite=True)
        self.assertEqual(json.loads(self.output.read_text()), [{"id": "001"}])

    def test_input_cannot_be_overwritten(self):
        self.write_source("id\n001\n")
        with self.assertRaisesRegex(converter.ConversionError, "different files"):
            converter.convert(self.source, self.source, overwrite=True)
        self.assertEqual(self.source.read_text(), "id\n001\n")

    def test_invalid_delimiters(self):
        self.write_source("id\n001\n")
        for delimiter in ["", "||", "\n", '"', "\0"]:
            with self.subTest(delimiter=delimiter):
                with self.assertRaisesRegex(converter.ConversionError, "delimiter"):
                    converter.convert(self.source, self.output, delimiter=delimiter)

    def test_header_only_file(self):
        self.write_source("id,name\n")
        converter.convert(self.source, self.output)
        self.assertEqual(self.output.read_text(), "[]\n")

    def test_cli_errors_are_readable_and_nonzero(self):
        self.write_source("a,a\n1,2\n")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = converter.main([str(self.source), str(self.output)])
        self.assertEqual(status, 1)
        self.assertIn("error: header names must be unique", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
