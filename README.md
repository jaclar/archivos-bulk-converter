# Archivos bulk converter

Python script to recursively run through a input directory
structure and find folders with `*.tif` files - usually document scans -
and convert them to PDF's with a watermark.

Currently this project is heavily scoped for the archive of the
[APDH](https://www.apdh.org.ar)

## Installation

1. Install Python 3.10, if not already installed
2. Install poetry: `pip install poetry`
3. Install dependencies: `poetry install`

## Run

(cli parameters are still TODO)
`poetry run start // $input_folder $output_folder`
