# ValidUPC

ValidUPC is a simple command line tool for validating Universal Product Codes (UPCs). It currently supports UPC-A, UPC-E, EAN-8, and EAN-13 barcode types.

## Features

- Reads UPC codes from CSV and TXT files.
- Supports both line and comma delimited files.
- Validates UPC codes according to their type.

## Installation

To install ValidUPC, first build the project and then install it using pip:

```bash
python -m build
pip install --force-reinstall dist/*.whl
```

## Usage
After installing, you can use ValidUPC from the command line to validate UPC codes in a file:
```bash 
validupc your_file.csv
```
This will validate all UPC codes in your_file.csv and print the results to the console.

Contributing
Contributions are welcome! Please feel free to submit a pull request.

License
MIT