
from abc import ABC, abstractmethod
from typing import Any, Optional, Union, List, Dict, Tuple

# Tipando os diversos tipos que pode ser 
DatasetType = Union[List[Any], Dict[Any, Any], Tuple[Any, ...]]


class BaseValidator(ABC):
    def __init__(self):
        self._dataset: Optional[DatasetType] = None
        
    @abstractmethod
    def load_dataset(self, path:str):
        """Carrega a fonte de dados de validação"""
        pass
    
    @abstractmethod
    def is_valid(self, value:str) -> Tuple[bool, str]:
        """Verifica se o valor está presente no dataset carregado."""
        pass
 
    def find_key_value(self,target_key:str , target_value:str) -> bool:
        """
        Pesquisa recursivamente em um JSON (dict ou list) por uma chave e valor específicos.
        Retorna True se encontrar, caso contrário, False.

        # --- Exemplo de Uso ---
        meu_json = {
            "id": 1,
            "metadata": {
                "source": "OpenAlex",
                "tags": [
                    {"type": "Journal", "code": "ABC-123"},
                    {"type": "Conference", "code": "XYZ-999"}
                ]
            }
        }

        existe = find_key_value(meu_json, "type", "Journal")
        print(f"Encontrou? {existe}") # Saída: True
        """
        if target_key == None or target_value == None:
            return False
        
        if target_key.strip() == '' or target_value.strip() == '':
            return False

        # Caso 1: Se for um dicionário
        if isinstance(self._dataset, dict):
            for key, value in self._dataset.items():
                # Verifica se é a chave e o valor que buscamos
                if str(key).lower() == target_key.lower() and str(value).lower() == target_value.lower():
                    return True
                
                # Se o valor for outra estrutura (dict ou list), mergulha nela
                if isinstance(value, (dict, list)):
                    if self.find_key_value(value, target_key, target_value):
                        return True

        # Caso 2: Se for uma lista
        elif isinstance(self._dataset, list):
            for item in self._dataset:
                # Se o item for outra estrutura, mergulha nela
                if isinstance(item, (dict, list)):
                    if self.find_key_value(item, target_key, target_value):
                        return True
                        
        return False

