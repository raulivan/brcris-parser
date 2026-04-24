# from xml.dom.minidom import Element
import xml.etree.ElementTree as ET
from .base_reader import BaseReader
from typing import List, Dict, Any

class XMLReader(BaseReader):
    def read(self, file_path: str) -> ET: # ET[Element[str]]:
        """
        Lê um arquivo XML e retorna um ElementTree
        """
        tree = ET.parse(file_path)
            
        return tree