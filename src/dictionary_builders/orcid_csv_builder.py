from abc import ABC
import json
import os
import csv
from typing import Tuple

from util.text_transformers import get_code_for_url


class OrcidCSVBuilder(ABC):
    def __init__(self):
        super().__init__()
        
    def make_csv_dataset(self, path:str):
       
        if not os.path.exists(path):
            raise FileNotFoundError(f"O arquivo de dados não foi encontrado: {path}")

        try:
            temp = None
            with open(path, mode='r', encoding='utf-8') as f:
                # O arquivo é um JSON array de objetos
                temp = list(csv.DictReader(f))
            
            with open('orcid_autoridade.csv', mode='w', newline='', encoding='utf-8') as arquivo:
                escritor = csv.writer(arquivo)
                escritor.writerow(['orcid', 'id'])

                for item in temp:
                    code = item['orcid']
                    if code is None or code.strip() == '':
                        continue
                    code = get_code_for_url(code)
                    id = item['id']

                    escritor.writerow([code, id])
            
           
            print(f"DataSet gerado com sucesso.")

        except json.JSONDecodeError:
            raise ValueError("Erro ao decodificar o arquivo. Verifique o formato.")
        except Exception as e:
            raise RuntimeError(f"Erro inesperado no carregamento de dados de ORCID: {e}")
    
    