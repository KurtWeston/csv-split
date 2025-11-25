"""Tests for CSVSplitter core functionality."""
import pytest
import csv
from pathlib import Path
from csv_split.splitter import CSVSplitter


@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file for testing."""
    csv_file = tmp_path / "test.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'age', 'city'])
        writer.writerow(['Alice', '30', 'NYC'])
        writer.writerow(['Bob', '25', 'LA'])
        writer.writerow(['Charlie', '35', 'NYC'])
        writer.writerow(['David', '28', 'LA'])
        writer.writerow(['Eve', '32', 'NYC'])
    return csv_file


@pytest.fixture
def quoted_csv(tmp_path):
    """CSV with quoted fields and commas."""
    csv_file = tmp_path / "quoted.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'address'])
        writer.writerow(['Alice', '123 Main St, Apt 4'])
        writer.writerow(['Bob', '456 "Oak" Ave'])
    return csv_file


class TestSplitByRows:
    def test_split_basic(self, sample_csv, tmp_path):
        splitter = CSVSplitter(str(sample_csv), ',', str(tmp_path))
        files = splitter.split_by_rows(2)
        
        assert len(files) == 3
        assert all(Path(f).exists() for f in files)
        
        with open(files[0], 'r') as f:
            lines = f.readlines()
            assert len(lines) == 3  # header + 2 rows
    
    def test_split_invalid_chunk_size(self, sample_csv, tmp_path):
        splitter = CSVSplitter(str(sample_csv), ',', str(tmp_path))
        
        with pytest.raises(ValueError, match='Chunk size must be positive'):
            splitter.split_by_rows(0)
        
        with pytest.raises(ValueError):
            splitter.split_by_rows(-5)
    
    def test_headers_preserved(self, sample_csv, tmp_path):
        splitter = CSVSplitter(str(sample_csv), ',', str(tmp_path))
        files = splitter.split_by_rows(2)
        
        for file in files:
            with open(file, 'r') as f:
                reader = csv.reader(f)
                headers = next(reader)
                assert headers == ['name', 'age', 'city']


class TestSplitBySize:
    def test_split_by_mb(self, sample_csv, tmp_path):
        splitter = CSVSplitter(str(sample_csv), ',', str(tmp_path))
        files = splitter.split_by_size('1MB')
        
        assert len(files) >= 1
        assert all(Path(f).exists() for f in files)
    
    def test_invalid_size_format(self, sample_csv, tmp_path):
        splitter = CSVSplitter(str(sample_csv), ',', str(tmp_path))
        
        with pytest.raises(ValueError, match='Size must be in format'):
            splitter.split_by_size('invalid')
        
        with pytest.raises(ValueError):
            splitter.split_by_size('10KB')


class TestSplitByColumn:
    def test_group_by_city(self, sample_csv, tmp_path):
        splitter = CSVSplitter(str(sample_csv), ',', str(tmp_path))
        files = splitter.split_by_column('city')
        
        assert len(files) == 2  # NYC and LA
        assert any('NYC' in f for f in files)
        assert any('LA' in f for f in files)
    
    def test_invalid_column(self, sample_csv, tmp_path):
        splitter = CSVSplitter(str(sample_csv), ',', str(tmp_path))
        
        with pytest.raises(ValueError, match='Column .* not found'):
            splitter.split_by_column('nonexistent')


class TestDelimiters:
    def test_custom_delimiter(self, tmp_path):
        csv_file = tmp_path / "pipe.csv"
        with open(csv_file, 'w') as f:
            f.write('name|age\n')
            f.write('Alice|30\n')
            f.write('Bob|25\n')
        
        splitter = CSVSplitter(str(csv_file), '|', str(tmp_path))
        files = splitter.split_by_rows(1)
        
        assert len(files) == 2
        with open(files[0], 'r') as f:
            content = f.read()
            assert '|' in content


class TestQuotedFields:
    def test_quoted_fields_preserved(self, quoted_csv, tmp_path):
        splitter = CSVSplitter(str(quoted_csv), ',', str(tmp_path))
        files = splitter.split_by_rows(2)
        
        with open(files[0], 'r') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            row = next(reader)
            assert row[1] == '123 Main St, Apt 4'
