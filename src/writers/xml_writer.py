import os
import re
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
            try:

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
                if ('relations' in record) and (len(record["relations"]) > 0):
                    relations_node = ET.SubElement(root, "relations")

                    for current_relation in record["relations"]:
                        
                        if not "attributes" in current_relation:
                            relation_node = ET.SubElement(relations_node, "relation", attrib=current_relation)
                        else:
                            current_relation_edit = current_relation.copy()
                            current_relation_edit.pop("attributes")

                            relation_node = ET.SubElement(relations_node, "relation", attrib=current_relation_edit)
                            relation_node_attributes = ET.SubElement(relation_node, "attributes")
                            for item in current_relation["attributes"]:
                                if item is None:
                                    continue
                                ET.SubElement(relation_node_attributes, "field", attrib=item)
                    

                    

                # Formata o XML para uma leitura mais fácil (pretty print)
                rough_string = ET.tostring(root, 'utf-8')
                rough_string_clean = self.clean_xml_string(rough_string)
                reparsed = minidom.parseString(rough_string_clean)
                pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")

                file_name = f"{uuid_based_identifier_generator()}.xml"
                sub_folder = f"lote_{file_name[0:2]}"
                sub_folder = sub_folder.upper()
                
                os.makedirs(os.path.join(file_path, sub_folder), exist_ok=True)
                
                output_path = os.path.join(file_path, sub_folder, file_name)
                
                print(f"Salvando o arquivo: {file_name}")
                
                with open(output_path, "wb") as f:
                    f.write(pretty_xml)
            except Exception as e:
                print(f"Erro ao escrever o arquivo XML: {e}")
                continue
    
    

    def clean_xml_string(self, content):
        if not isinstance(content, str):
            return content
        # Remove caracteres de controle ilegais no XML (0x00-0x08, 0x0B, 0x0C, 0x0E-0x1F)
        # Mantém apenas os válidos: \x09 (tab), \x0A (newline), \x0D (carriage return)
        illegal_xml_chars = re.compile(
            u'[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]'
        )
        return illegal_xml_chars.sub('', content)