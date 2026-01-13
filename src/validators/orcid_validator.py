import json
import os
import csv
from typing import Dict, List, Tuple

from util.text_transformers import get_code_for_url

from .base_validator import BaseValidator, DatasetType

class OrcidValidator(BaseValidator):
    def __init__(self):
        super().__init__()
        
    def load_dataset(self, path:str):
        """
        Lê o arquivo CSV, constrói o mapeamento {name: code} e armazena em self._dataset.
        Garante que a chave (name) seja limpa (strip/lower) para otimizar a busca.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"O arquivo de dados não foi encontrado: {path}")

        try:
            temp = None
            with open(path, mode='r', encoding='utf-8') as f:
                # O arquivo é um JSON array de objetos
                temp = list(csv.DictReader(f))
            

            mapping: DatasetType = {}
            for item in temp:
                code = item['orcid']
                if code is None or code.strip() == '':
                    continue
                # code = get_code_for_url(code)
                id = item['id']
                mapping[code] = id
            
            self._dataset = mapping
            print(f"ORCID carregadas com sucesso. Total de {len(self._dataset)} entradas.")

        except json.JSONDecodeError:
            raise ValueError("Erro ao decodificar o arquivo JSON de ORCID. Verifique o formato.")
        except Exception as e:
            raise RuntimeError(f"Erro inesperado no carregamento de dados de ORCID: {e}")
    
    def is_valid(self, description: str) -> Tuple[bool, str]:
        """
        Recebe uma descrição string e verifica se o nome existe como chave no dataset.
        Retorna o 'code' correspondente se for válido.
        """
        if self._dataset is None:
            raise RuntimeError("O dataset não foi carregado. Execute load_dataset() primeiro.")
            
        if not description:
            return False, None
        
        search_key = description.strip().lower()

        # self._dataset é o dict {name: code}
        found_code = self._dataset.get(search_key)
        
        # Retorna o código (str) ou None
        return found_code is not None, found_code