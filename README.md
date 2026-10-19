# CSV to JSON — personal demonstration

**Personal demonstration, no client engagement.** All example data is synthetic.
This small Python command-line tool demonstrates a data conversion workflow with
explicit validation and protected output files. It uses only the Python standard
library and makes no network requests.

## Small paid Python tasks

A small CSV/JSON cleanup or conversion task is **$40 fixed**, delivered within
**2 days** after scope, materials, access and payment timing are agreed.
Typical scope: one input file up to 50,000 rows / 20 MB, up to five agreed
transformation rules, and one output format. Delivery includes editable source,
run instructions, checks for normal, malformed and repeated input, and one
in-scope revision.

[Open a task inquiry](https://github.com/brodyga45/freelance-csv-json-example-20261019/issues/new)
with the input shape, expected output and deadline. Use invented sample rows in
public issues. The exact deliverable and acceptance checks are agreed before work
starts; an inquiry does not place an order.

Work and written correspondence are AI-assisted on behalf of this account's
owner, a Serbian sole proprietor. The code below is a personal example, rather
than a paid client case study.

Another personal source example: [HTML/CSS/JavaScript interactions](https://github.com/brodyga45/freelance-csv-json-example-20261019/tree/main/frontend-source).

## Run

Requires Python 3.9 or newer. Run these commands from this directory:

```sh
python3 csv_to_json.py examples/contacts.csv /tmp/demo-contacts.json
python3 csv_to_json.py examples/products-semicolon.csv /tmp/demo-products.json --delimiter ';'
python3 -m unittest -v
```

The checked-in `.json` files show the expected outputs for the accompanying CSVs.
If the chosen output already exists, select another path or add `--overwrite`.
The output directory must already exist. Errors print `error: ...` to stderr and
return exit status 1; successful conversion returns 0 and reports the record count.

## Conversion rules

- Read UTF-8, with or without a UTF-8 BOM; write readable UTF-8 JSON.
- Use the first CSV record as object keys. Reject empty or whitespace-only keys
  and exact duplicate keys. Preserve other header whitespace and case.
- Preserve every cell as a string, including leading zeros, decimal formatting,
  empty values and text that resembles booleans. Do not guess data types.
- Reject records with missing or extra cells, including blank records. Report
  the physical line where the problematic record ends.
- Support a single-character delimiter and standard double-quoted fields,
  including quoted separators and multiline text. Use Python's strict CSV parser
  to reject malformed quoting that it detects.
- A header-only CSV produces an empty array. An empty file is an error.

## Output protection and limits

All records are validated and serialized before creating output. A temporary
file in the output directory is flushed and then published atomically. By
default, a hard link creates the destination only if it does not exist, including
when another process creates it during conversion. `--overwrite` uses atomic
replacement after validation. Input and output must be different paths; resolved
symlink aliases are rejected. Existing output stays intact after validation errors.

The complete dataset is held in memory, so this example is intended for small
files rather than large streaming imports. It does not auto-detect delimiters or
encodings, normalize headers, repair rows, enforce a business schema, or sanitize
values for spreadsheet use. CSV syntax follows Python's `csv` dialect rather than
a custom parser. Atomic publishing requires a filesystem that supports hard links
and same-directory replacement; unsupported operations return an error. Output
uses temporary-file permissions and does not preserve old file metadata. The tool
does not provide a power-loss durability guarantee for the directory entry.

The unit tests cover BOM/Unicode, leading zeros, quoted multiline fields,
malformed headers/rows/quoting, invalid UTF-8, output protection (including a
concurrent creation), explicit overwrite, source protection and CLI error reporting.

## Provenance

Self-authored personal example, developed with AI assistance. The example data is synthetic; this is not a client delivery or a claim of past paid work. Published for code inspection alongside a freelance data-processing offer.
