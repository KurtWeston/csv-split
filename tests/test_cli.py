"""Tests for CLI interface."""
import pytest
from click.testing import CliRunner
from csv_split.cli import main
import csv
from pathlib import Path


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_csv(tmp_path):
    csv_file = tmp_path / "test.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'age', 'city'])
        for i in range(10):
            writer.writerow([f'Person{i}', str(20 + i), 'NYC'])
    return csv_file


class TestCLI:
    def test_split_by_rows(self, runner, sample_csv):
        result = runner.invoke(main, [str(sample_csv), '--rows', '3'])
        
        assert result.exit_code == 0
        assert 'Successfully created' in result.output
    
    def test_split_by_size(self, runner, sample_csv):
        result = runner.invoke(main, [str(sample_csv), '--size', '1MB'])
        
        assert result.exit_code == 0
        assert 'Successfully created' in result.output
    
    def test_split_by_group(self, runner, sample_csv):
        result = runner.invoke(main, [str(sample_csv), '--group-by', 'city'])
        
        assert result.exit_code == 0
        assert 'Successfully created' in result.output
    
    def test_no_split_option(self, runner, sample_csv):
        result = runner.invoke(main, [str(sample_csv)])
        
        assert result.exit_code != 0
        assert 'Specify exactly one' in result.output
    
    def test_multiple_split_options(self, runner, sample_csv):
        result = runner.invoke(main, [str(sample_csv), '--rows', '5', '--size', '1MB'])
        
        assert result.exit_code != 0
        assert 'Specify exactly one' in result.output
    
    def test_output_dir(self, runner, sample_csv, tmp_path):
        output_dir = tmp_path / "output"
        result = runner.invoke(main, [
            str(sample_csv),
            '--rows', '5',
            '--output-dir', str(output_dir)
        ])
        
        assert result.exit_code == 0
        assert output_dir.exists()
    
    def test_custom_delimiter(self, runner, tmp_path):
        csv_file = tmp_path / "pipe.csv"
        with open(csv_file, 'w') as f:
            f.write('name|age\n')
            f.write('Alice|30\n')
            f.write('Bob|25\n')
        
        result = runner.invoke(main, [
            str(csv_file),
            '--rows', '1',
            '--delimiter', '|'
        ])
        
        assert result.exit_code == 0
    
    def test_nonexistent_file(self, runner):
        result = runner.invoke(main, ['nonexistent.csv', '--rows', '5'])
        
        assert result.exit_code != 0
