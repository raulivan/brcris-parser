import csv
from .base_writer import BaseWriter

class CSVWriter(BaseWriter):
    def write(self, records: list[dict], file_path: str):
        """Escreve uma lista de dicionários em um arquivo CSV."""
        if not records:
            return
        
        keys = records[0].keys()
        with open(file_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(records)