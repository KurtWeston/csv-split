"""CLI interface for csv-split tool."""
import click
import os
from pathlib import Path
from .splitter import CSVSplitter


@click.command()
@click.argument('input_file', type=click.Path(exists=True, readable=True))
@click.option('--rows', type=int, help='Split by number of rows per file')
@click.option('--size', type=str, help='Split by file size (e.g., 10MB, 1GB)')
@click.option('--group-by', type=str, help='Column name to group rows by')
@click.option('--delimiter', default=',', help='CSV delimiter (default: comma)')
@click.option('--output-dir', type=click.Path(), help='Output directory for split files')
def main(input_file, rows, size, group_by, delimiter, output_dir):
    """Split large CSV files into smaller chunks.
    
    Split by rows, file size, or column values. Preserves headers in all output files.
    """
    if sum([bool(rows), bool(size), bool(group_by)]) != 1:
        raise click.UsageError('Specify exactly one of: --rows, --size, or --group-by')
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = os.path.dirname(input_file) or '.'
    
    splitter = CSVSplitter(input_file, delimiter, output_dir)
    
    try:
        if rows:
            files = splitter.split_by_rows(rows)
        elif size:
            files = splitter.split_by_size(size)
        elif group_by:
            files = splitter.split_by_column(group_by)
        
        click.echo(f"\nSuccessfully created {len(files)} files:")
        for f in files:
            click.echo(f"  - {f}")
    except Exception as e:
        raise click.ClickException(str(e))


if __name__ == '__main__':
    main()