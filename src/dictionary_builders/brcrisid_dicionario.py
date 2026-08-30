import os
import csv
import xml.etree.ElementTree as ET

from .base_dictionary_builders import BaseDictionaryBuilder
from tqdm import tqdm

class BrCrisIdDicionario(BaseDictionaryBuilder):
    def process_xml_files(self, source_path, output_path, entity_type):
        brcrisid_list = []

        print(f"Iniciando varredura em: {source_path}")

        for root, dirs, files in os.walk(source_path):
            for file in files:
                if file.endswith(".xml"):
                    file_path = os.path.join(root, file)
                    
                    try:
                        tree = ET.parse(file_path)
                        xml_root = tree.getroot()

                        for entity in xml_root.findall(f".//entity[@type='{entity_type}']"):
                            
                            # Recupera o semanticIdentifier
                            semantic_id_list = entity.findall("semanticIdentifier")
                            for semantic_id_elem in semantic_id_list:
                                code = semantic_id_elem.text if semantic_id_elem is not None else None
                                print(f"Indexando BrCrisId: {code}")
                                # Só adiciona se ambos os campos existirem
                                if code:
                                    code = code.replace('brcris::','')

                                    brcrisid_list.append(code.strip())

                    except Exception as e:
                        print(f"Erro ao processar arquivo {file_path}: {e}")

        try:
            brcrisid_list_distinct = list(set(brcrisid_list))

            with open(output_path, 'w', newline='', encoding='utf-8') as arquivo:
                escritor = csv.writer(arquivo)

                for item in brcrisid_list_distinct:
                    print(f"Persistindo o BrCrisId: {item}")
                    escritor.writerow([item])
            print(f"\nSucesso! {len(brcrisid_list_distinct)} registros salvos em: {output_path}")
        
        except Exception as e:
            print(f"Erro ao salvar o arquivo JSON: {e}")
