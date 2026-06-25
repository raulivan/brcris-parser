import json
import os
from typing import Generator
from .base_reader import BaseReader
from pathlib import Path

class MapJsonFilePathReader(BaseReader):
    def read(self, file_path: str) -> Generator[dict, None, None]:
        """
        Usando quando precisa mapear arquivos diferentes para um mesmo registro a ser carregado
        """
        try:
            for pasta_atual, sub_pastas, arquivos in os.walk(file_path):
                retorno  = {
                    "raiz": file_path,
                    "pasta_atual": pasta_atual,
                    "sub_pastas": sub_pastas,
                    "arquivos": arquivos
                }
                yield retorno
        except FileNotFoundError:
            raise FileNotFoundError(f"Erro: Arquivo {file_path} não encontrado.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao decodificar JSON no arquivo {file_path}: {e}")

# import json
# from .base_reader import BaseReader

# class JSONLReader(BaseReader):
#     def read(self, file_path: str) -> list[str]:
#         """Lê um arquivo JSON (contendo uma lista de objetos) e o retorna."""
#         arq = open(file_path, 'rb')
       
#         registros = arq.readlines()
#         return registros