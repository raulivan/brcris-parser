import gzip
import json
from typing import Generator
from .base_reader import BaseReader

class JSONLGZReader(BaseReader):
    def read(self, file_path: str) -> Generator[dict, None, None]:
        """
        Abre um arquivo .gz e lê cada linha como um objeto JSON 
        usando um gerador para economia de memória.
        """
        # "rt" significa: r (read) e t (text mode), essencial para ler strings
        try:
            with gzip.open(file_path, mode="rt", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.strip()
                    if linha:
                        try:
                            yield linha
                        except json.JSONDecodeError as e:
                            print(f"Erro ao processar linha no arquivo {file_path}: {e}")
                            continue
        except Exception as e:
            raise ValueError(f"Erro ao abrir arquivo compactado {file_path}: {e}")
# import gzip
# from .base_reader import BaseReader

# class JSONLGZReader(BaseReader):
#     def read(self, file_path: str) -> list[str]:
#         """Lê um arquivo JSON (contendo uma lista de objetos) e o retorna."""
#         with gzip.open(file_path, mode="rt", encoding="utf-8") as f:
            
#             registros = f.readlines()
#             return registros
    
