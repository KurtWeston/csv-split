"""Core CSV splitting logic."""
import csv
import os
from pathlib import Path
from typing import List, Dict
import re


class CSVSplitter:
    def __init__(self, input_file: str, delimiter: str = ',', output_dir: str = '.'):
        self.input_file = Path(input_file)
        self.delimiter = delimiter
        self.output_dir = Path(output_dir)
        self.base_name = self.input_file.stem
        self.headers = None
        
    def _read_headers(self):
        """Read and cache CSV headers."""
        if self.headers is None:
            with open(self.input_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=self.delimiter)
                self.headers = next(reader)
        return self.headers
    
    def _write_chunk(self, filename: str, rows: List[List[str]]) -> str:
        """Write rows to output file with headers."""
        output_path = self.output_dir / filename
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=self.delimiter)
            writer.writerow(self.headers)
            writer.writerows(rows)
        return str(output_path)
    
    def split_by_rows(self, chunk_size: int) -> List[str]:
        """Split CSV by number of rows per file."""
        if chunk_size <= 0:
            raise ValueError('Chunk size must be positive')
        
        self._read_headers()
        output_files = []
        chunk_num = 1
        current_chunk = []
        
        with open(self.input_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            next(reader)  # Skip header
            
            for row in reader:
                current_chunk.append(row)
                
                if len(current_chunk) >= chunk_size:
                    filename = f"{self.base_name}_part{chunk_num:03d}.csv"
                    output_files.append(self._write_chunk(filename, current_chunk))
                    current_chunk = []
                    chunk_num += 1
            
            if current_chunk:
                filename = f"{self.base_name}_part{chunk_num:03d}.csv"
                output_files.append(self._write_chunk(filename, current_chunk))
        
        return output_files
    
    def split_by_size(self, size_str: str) -> List[str]:
        """Split CSV by target file size (e.g., '10MB', '1GB')."""
        match = re.match(r'^(\d+(?:\.\d+)?)(MB|GB)$', size_str.upper())
        if not match:
            raise ValueError('Size must be in format: 10MB or 1GB')
        
        value, unit = match.groups()
        target_bytes = float(value) * (1024 * 1024 if unit == 'MB' else 1024 * 1024 * 1024)
        
        self._read_headers()
        output_files = []
        chunk_num = 1
        current_chunk = []
        current_size = 0
        header_size = len(','.join(self.headers).encode('utf-8'))
        
        with open(self.input_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            next(reader)
            
            for row in reader:
                row_size = len(self.delimiter.join(row).encode('utf-8'))
                
                if current_size + row_size + header_size > target_bytes and current_chunk:
                    filename = f"{self.base_name}_part{chunk_num:03d}.csv"
                    output_files.append(self._write_chunk(filename, current_chunk))
                    current_chunk = []
                    current_size = 0
                    chunk_num += 1
                
                current_chunk.append(row)
                current_size += row_size
            
            if current_chunk:
                filename = f"{self.base_name}_part{chunk_num:03d}.csv"
                output_files.append(self._write_chunk(filename, current_chunk))
        
        return output_files
    
    def split_by_column(self, column_name: str) -> List[str]:
        """Split CSV by unique values in specified column."""
        self._read_headers()
        
        if column_name not in self.headers:
            raise ValueError(f"Column '{column_name}' not found in CSV headers")
        
        col_index = self.headers.index(column_name)
        groups: Dict[str, List[List[str]]] = {}
        
        with open(self.input_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            next(reader)
            
            for row in reader:
                if col_index < len(row):
                    key = row[col_index] or 'empty'
                    key = re.sub(r'[^\w\-]', '_', key)[:50]
                    
                    if key not in groups:
                        groups[key] = []
                    groups[key].append(row)
        
        output_files = []
        for key, rows in groups.items():
            filename = f"{self.base_name}_{key}.csv"
            output_files.append(self._write_chunk(filename, rows))
        
        return output_files