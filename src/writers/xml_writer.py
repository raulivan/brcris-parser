import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

from util.unique_identifier_generator import uuid_based_identifier_generator
from .base_writer import BaseWriter

class XMLWriter(BaseWriter):
    def write(self,source:str, records: list[dict], file_path: str):
        """
        Escreve uma lista de dicionários em um arquivo XML estruturado.
        Cada dicionário na lista 'records' deve ter a estrutura necessária
        para criar uma entidade <entity>.
        """
        if not records:
            return

        
        # Itera sobre os registros preparados pelo mapper
        for record in records:
            # Cria o elemento raiz <entity-relation-data> do arquivo
            root_attributes = {
                "lastUpdate": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "source": source,
                "record": self.creat_record_identifier()
            }
            root = ET.Element("entity-relation-data", root_attributes)
            
            # TAG Entidades
            entities_node = ET.SubElement(root, "entities")

            for current_entity in record["entities"]:
                
                entity_node = ET.SubElement(entities_node, "entity", attrib=current_entity["entity_attribs"])
                
                # Adiciona os identificadores semânticos (<semanticIdentifier>) para cada entidade
                for field_data in current_entity["semantic_identifiers"]:
                    semanticIdentifier = ET.SubElement(entity_node, "semanticIdentifier")
                    semanticIdentifier.text = field_data['value']

                # Adiciona os campos (<field>) que são identificadores cada entidade
                for field_data in current_entity["fields_identifier"]:
                    ET.SubElement(entity_node, "field", attrib=field_data)
                    
                # Adiciona os campos (<field>) para cada entidade
                for field_data in current_entity["fields"]:
                    if isinstance(field_data['value'], dict):
                        campo_complexo = ET.SubElement(entity_node, "field", attrib={'name': field_data['name']})
                        for field_name, field_value in field_data['value'].items():
                            ET.SubElement(campo_complexo, "field", attrib={'name': field_name, 'value': field_value})
                    else:
                        ET.SubElement(entity_node, "field", attrib=field_data)
            
            
            # TAG Relacionamentos
            relations_node = ET.SubElement(root, "relations")

            for current_relation in record["relations"]:
                relation_node = ET.SubElement(relations_node, "relation", attrib=current_relation)
                

            # Formata o XML para uma leitura mais fácil (pretty print)
            rough_string = ET.tostring(root, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")

            file_name = f"{uuid_based_identifier_generator()}.xml"
            sub_folder = f"lote_{file_name[0:2]}"
            sub_folder = sub_folder.upper()
            
            os.makedirs(os.path.join(file_path, sub_folder), exist_ok=True)
            
            output_path = os.path.join(file_path, sub_folder, file_name)
            
            print(f"Salvando o arquivo: {file_name}")
            
            with open(output_path, "wb") as f:
                f.write(pretty_xml)