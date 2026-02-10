# ValidUPC

ValidUPC is a command line tool for validating, generating, and reading barcodes. It supports UPC-A, UPC-E, EAN-8, EAN-13, and QR code formats.

## Features

- **Validate** UPC codes from CSV/TXT files or stdin.
- **Generate** barcode and QR code images (PNG or SVG).
- **Read** barcodes and QR codes from image files.
- Supports UPC-A, UPC-E, EAN-8, EAN-13, and QR codes.
- No external barcode/QR libraries required (only Pillow for image handling).

## Installation

Build and install with pip:

```bash
python -m build
pip install --force-reinstall dist/*.whl
```

Or install in editable mode for development:

```bash
pip install -e .
```

### Docker

```bash
docker build -t validupc .
docker run --rm validupc ValidUPC -h
```

## Usage

### Validate barcodes

Read codes from a file and validate them:

```bash
ValidUPC validate -i barcodes.csv -t UPC_A
```

Read from stdin:

```bash
echo "123456789012" | ValidUPC validate -t UPC_A
```

### Generate barcode images

```bash
# UPC-A barcode
ValidUPC generate -c 123456789104 -t UPC_A -o my_barcode

# EAN-13 barcode as SVG
ValidUPC generate -c 1111111111116 -t EAN_13 -o my_ean --format svg

# QR code
ValidUPC generate -c "https://example.com" -t QR -o my_qr
```

### Read barcodes from images

```bash
# Auto-detect barcode type
ValidUPC read -i my_barcode.png

# Specify expected type
ValidUPC read -i my_ean.png -t EAN_13

# Read QR code
ValidUPC read -i my_qr.png -t QR
```

## Supported Barcode Types

| Type | Digits | Example |
|------|--------|---------|
| UPC_A | 12 | 123456789012 |
| UPC_E | 7 | 1234561 |
| EAN_8 | 8 | 55123457 |
| EAN_13 | 13 | 1111111111116 |
| QR | N/A | Any text or URL |

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

MIT
