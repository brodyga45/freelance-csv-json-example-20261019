#!/usr/bin/env python3
"""Convert a UTF-8 CSV file to an array of JSON objects, without type guessing."""

import argparse
import csv
import json
import os
from pathlib import Path
import sys
import tempfile


class ConversionError(ValueError):
    """A readable input or output validation error."""


def read_records(source, delimiter=","):
    if len(delimiter) != 1 or delimiter in '\r\n"\0':
        raise ConversionError("delimiter must be one character other than a quote, NUL or newline")
    records = []
    with Path(source).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, delimiter=delimiter, strict=True)
        try:
            headers = next(reader, None)
            if not headers:
                raise ConversionError("CSV must contain a header row")
            if any(not header.strip() for header in headers):
                raise ConversionError("header names must not be empty or whitespace-only")
            if len(set(headers)) != len(headers):
                raise ConversionError("header names must be unique")
            for cells in reader:
                if len(cells) != len(headers):
                    raise ConversionError(
                        f"CSV record ending on line {reader.line_num}: "
                        f"expected {len(headers)} cells, found {len(cells)}"
                    )
                records.append(dict(zip(headers, cells)))
        except csv.Error as exc:
            raise ConversionError(f"invalid CSV near line {reader.line_num}: {exc}") from exc
    return records


def convert(source, destination, delimiter=",", overwrite=False):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ConversionError("input and output must be different files")
    if not overwrite and (destination.exists() or destination.is_symlink()):
        raise ConversionError("output already exists; choose another path or use --overwrite")
    records = read_records(source, delimiter)
    # Validate and serialize everything before touching the destination.
    payload = json.dumps(records, ensure_ascii=False, indent=2) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=destination.parent,
            prefix=".csv-json-", suffix=".tmp", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if overwrite:
            os.replace(temporary, destination)
        else:
            # Atomic creation: even an output created during conversion is protected.
            try:
                os.link(temporary, destination)
            except FileExistsError as exc:
                raise ConversionError("output already exists; choose another path or use --overwrite") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return len(records)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="CSV file encoded as UTF-8 (optional BOM)")
    parser.add_argument("output", type=Path, help="destination JSON file")
    parser.add_argument("--delimiter", default=",", help="single-character separator; default: comma")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing output file")
    args = parser.parse_args(argv)
    try:
        count = convert(args.input, args.output, args.delimiter, args.overwrite)
    except (ConversionError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {count} records to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
