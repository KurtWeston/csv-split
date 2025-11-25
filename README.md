# csv-split

A CLI tool that intelligently splits large CSV files into smaller chunks based on row count, file size, or column values

## Features

- Split CSV files by number of rows with configurable chunk size
- Split CSV files by target file size in MB/GB
- Group rows by column value to create separate files per unique value
- Automatically preserve CSV headers in all output files
- Correctly handle quoted fields, commas within quotes, and escaped delimiters
- Support custom delimiters (comma, tab, semicolon, pipe)
- Generate output files with numbered suffixes or column-value-based names
- Display progress bar for large file processing
- Validate input file exists and is readable CSV format
- Option to specify output directory for split files

## Installation

```bash
# Clone the repository
git clone https://github.com/KurtWeston/csv-split.git
cd csv-split

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Built With

- python using click

## Dependencies

- `click>=8.0.0`
- `pytest>=7.0.0`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
