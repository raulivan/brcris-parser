from abc import ABC, abstractmethod

from util.unique_identifier_generator import uuid_based_identifier_generator

class BaseWriter(ABC):
    @abstractmethod
    def write(self, source:str, records: list[dict], file_path: str):
        """Escreve os registros transformados em um arquivo."""
        pass
    
    def creat_record_identifier(self) -> str:
        return uuid_based_identifier_generator()