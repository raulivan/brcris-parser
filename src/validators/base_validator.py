
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
    
