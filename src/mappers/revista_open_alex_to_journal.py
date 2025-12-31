import json
from typing import List
from validators.base_validator import BaseValidator
from util.unique_identifier_generator import brcrisid_generator
from util.text_transformers import capitalizar_nome, get_code_for_url, trata_string
from .base_mapper import BaseMapper



class RevistaOpenAlex2JournalMapper(BaseMapper):
    def get_source(self) -> str:
        return "OpenAlex"

    def transform(self, records: list[dict], validators: List[BaseValidator] = []) -> list[dict]:
        """
        Converte registros de entrada para uma estrutura de dicionário
        pronta para ser convertida em XML pelo XMLWriter.
        """
        if records is None:
            return None
        
        # Tuplas de controle de campos
        
        # Relacionamento com cursos
        transformed_records = []

       
        
        # Montando a lista de registros para Iteração
        # records_loop = records if len(records) == 1 else [records]
        for record_string in records:
            
            # Identificador semanticos 
            journal_SemanticIdentifiers_tupla = []
            # Campos Identificador
            journal_fields_identifier_tupla = []
            # Campos field
            journal_fields_tupla = []
            
            if record_string == None or len(record_string.strip()) == 0:
                continue
            
            
            
            # Gerando a referência deste registro para relacionamentos
            journal_ref = self.creat_ref_identifier()
            print(f"Processando registro: {journal_ref}")
            
            record =  json.loads(record_string)
            record_node_ids = self.get_field_value(record, "ids")
             
            #********************** <field name="identifier.issn" description="ISSN"/> 
            tem_tag_issn = False
            node_issn = self.get_field_value(record, 'issn')
            if self.has_value(node_issn):
                for item_issn in node_issn:
                    if not self.has_value(item_issn):
                        continue
                    
                    tem_tag_issn = True
                    item_issn_sem_espacos = trata_string(item_issn)
                    
                    brcris_id_v1 = brcrisid_generator(item_issn_sem_espacos)
                    brcris_id_v2 = brcrisid_generator(item_issn_sem_espacos,useReplaceHtmlChars=True)
                    
                    journal_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}"))
                    journal_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
                    if brcris_id_v1 != brcris_id_v2:
                        journal_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v2}v2"))
                        journal_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v2}v2"))

                    journal_SemanticIdentifiers_tupla.append(("issn", f"issn::{item_issn_sem_espacos}"))
                    journal_fields_identifier_tupla.append(("identifier.issn", item_issn_sem_espacos))

            if tem_tag_issn == False:
                if self.has_value(record_node_ids):
                    for item_ids_key, item_ids_value  in record_node_ids.items():
                        if item_ids_key == 'issn':
                            if isinstance(item_ids_value, list):
                                for item_issn in item_ids_value:
                                    if not self.has_value(item_issn):
                                        continue
                        
                                    item_issn_sem_espacos = trata_string(item_issn)
                            
                                    brcris_id_v1 = brcrisid_generator(item_issn_sem_espacos)
                                    brcris_id_v2 = brcrisid_generator(item_issn_sem_espacos,useReplaceHtmlChars=True)
                                    
                                    journal_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}"))
                                    journal_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
                                    if brcris_id_v1 != brcris_id_v2:
                                        journal_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}v2"))
                                        journal_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v1}v2"))

                                    journal_SemanticIdentifiers_tupla.append(("issn", f"issn::{item_issn_sem_espacos}"))
                                    journal_fields_identifier_tupla.append(("identifier.issn", item_issn_sem_espacos))
                            else:
                                if self.has_value(item_ids_value):
                                                            
                                    item_issn_sem_espacos = trata_string(item_ids_value)
                            
                                    brcris_id_v1 = brcrisid_generator(item_issn_sem_espacos)
                                    brcris_id_v2 = brcrisid_generator(item_issn_sem_espacos,useReplaceHtmlChars=True)
                                    
                                    journal_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}"))
                                    journal_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
                                    if brcris_id_v1 != brcris_id_v2:
                                        journal_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}v2"))
                                        journal_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v1}v2"))

                                    journal_SemanticIdentifiers_tupla.append(("issn", f"issn::{item_issn_sem_espacos}"))
                                    journal_fields_identifier_tupla.append(("identifier.issn", item_issn_sem_espacos))
                                
            #********************** <field name="identifier.issn_l" description="ISSN-L"/>
            if self.has_value(record_node_ids):
                for item_ids_key, item_ids_value  in record_node_ids.items():
                    if item_ids_key == 'issn_l':
                        if isinstance(item_ids_value, list):
                            for item_issnl in item_ids_value:
                                if not self.has_value(item_issnl):
                                    continue
                                journal_fields_identifier_tupla.append(("identifier.issn_l", trata_string(item_issnl)))
                        else:
                            if self.has_value(item_ids_value):
                                journal_fields_identifier_tupla.append(("identifier.issn_l", trata_string(item_ids_value)))

            #********************** <field name="identifier.openalex" description="Identificação da revista na OpenAlex"/>
            if self.has_value(record_node_ids):
                for item_ids_key, item_ids_value  in record_node_ids.items():
                    if item_ids_key == 'openalex':
                        if not self.has_value(item_ids_value):
                             continue
                        journal_fields_identifier_tupla.append(("identifier.openalex", get_code_for_url(trata_string(item_ids_value))))
                        journal_SemanticIdentifiers_tupla.append(("openalex", f"openalex::{get_code_for_url(trata_string(item_ids_value))}"))
                        
   
            #********************** <field name="title" description="título da revista"/> <!-- testar api de padronizacao do Rene?? -->
            journal_name = self.get_field_value(record, "title")
            if journal_name is not None:
                journal_name = capitalizar_nome(journal_name)
                journal_fields_tupla.append(("title", journal_name))
            
            journal_display_name = self.get_field_value(record, "display_name")
            if journal_display_name is not None:
                journal_display_name = capitalizar_nome(journal_display_name)
                journal_fields_tupla.append(("title", journal_display_name))
            
            json_node_alternate_titles =  self.get_field_value(record, 'alternate_titles')
            if self.has_value(json_node_alternate_titles):
                for item in json_node_alternate_titles:
                    if item is not None:
                        journal_alternative_name = capitalizar_nome(item)
                        journal_fields_tupla.append(("title", journal_alternative_name))
                        
            #********************** <field name="publisher" description="Quem publica a revista"/> <!-- testar api de padronizacao do Rene?? -->
            json_node_publisher_nome = self.get_field_value(record, 'publisher')
            if self.has_value(json_node_publisher_nome):
                publisher_name = capitalizar_nome(json_node_publisher_nome)
                journal_fields_tupla.append(("publisher", publisher_name))
                
            #********************** <field name="websiteURL" description="url da revista"/>
            json_node_homepage_url = self.get_field_value(record, 'homepage_url')
            if self.has_value(json_node_homepage_url):
                journal_fields_tupla.append(("websiteURL", trata_string(json_node_homepage_url)))
                

            #********************** <field name="isOa" description="Verifica se a revista é Oa (True ou False)"/>
            json_node_is_oa = self.get_field_value(record, 'is_oa')
            if self.has_value(json_node_is_oa):
                journal_fields_tupla.append(("isOa", str(json_node_is_oa)))
                
            
            #********************** <field name="isInDoaj" description="Verifica se a revista está no Doaj (True ou False)"/>
            json_node_is_in_doaj = self.get_field_value(record, 'is_in_doaj')
            if  self.has_value(json_node_is_in_doaj):
                journal_fields_tupla.append(("isInDoaj", str(json_node_is_in_doaj)))
            
            #********************** <field name="apcCost" description="Taxa de Processamento de Artigos">
                                    # 	<field name="apcAmount" description="Valor da revista (APC)"/>
                                    # 	<field name="apcCurrency" description="Moeda do APC"/>
                                    # </field>
            
            json_node_apc_prices = self.get_field_value(record, 'apc_prices')
            if self.has_value(json_node_apc_prices):
                for item in json_node_apc_prices:
                    apcCost = {
                        "apcAmount": str(self.get_field_value(item, 'price')),
                        "apcCurrency": str(self.get_field_value(item, 'currency'))
                    }
                    journal_fields_tupla.append(("apcCost", apcCost))
                    
            
            #********************** <field name="countryCode" description="Código do país"/>
            json_node_country_code =  self.get_field_value(record, 'country_code')
            if self.has_value(json_node_country_code):
                journal_fields_tupla.append(("countryCode", trata_string(json_node_country_code)))
            
            #********************** <field name="type" description="Tipo de publicação"/>
            json_node_type = self.get_field_value(record, 'type')
            if self.has_value(json_node_type):
                journal_fields_tupla.append(("type", trata_string(json_node_type)))
                
            #********************** <field name="assessmentArea" description="Área da Revista"/>
            json_node_areas_avaliacao = self.get_field_value(record, 'areas_avaliacao')
            if self.has_value(json_node_areas_avaliacao):
                for item in json_node_areas_avaliacao:
                    journal_fields_tupla.append(("assessmentArea", trata_string(item)))
            
            #********************** <field name="qualis" description="Qualis da Revista"/>
            json_node_estrato = self.get_field_value(record, 'estrato')
            if self.has_value(json_node_estrato):
                journal_fields_tupla.append(("qualis", trata_string(json_node_estrato)))
            
            #********************** <field name="keywords" description="Palavras chave "/> <!-- testar api de padronizacao do Rene?? -->
            # NÃO TEM
            
            #********************** <field name="2yr_mean_citedness" description="média de citação"/>
            json_node_summary_stats = self.get_field_value(record, 'summary_stats')
            if self.has_value(json_node_summary_stats) :
                summary_stats = self.get_field_value(json_node_summary_stats, '2yr_mean_citedness')
                if self.has_value(summary_stats) :
                    journal_fields_tupla.append(("2yr_mean_citedness", str(summary_stats)))
            
            
            #********************** <field name="h_index" description="índice h"/>
            if self.has_value(json_node_summary_stats) :
                h_index = self.get_field_value(json_node_summary_stats,'h_index')
                if self.has_value(h_index) :
                    journal_fields_tupla.append(("h_index", str(h_index))) 
                    
            #********************** <field name="i10_index" description="índice i10"/>
            if self.has_value(json_node_summary_stats) :
                i10_index = self.get_field_value(json_node_summary_stats,'i10_index')
                if self.has_value(i10_index) :
                    journal_fields_tupla.append(("i10_index", str(i10_index))) 
                    
            #********************** <field name="googleH5" description="Google Scholar H5"/>
            
            
            new_entity_journal = {
                "entity_attribs": {
                    "type": "Journal",
                    "ref": journal_ref
                },
                "semantic_identifiers":[
                    {"name": name, "value": value} for name, value in journal_SemanticIdentifiers_tupla if value is not None
                ],
                "fields_identifier": [
                    {"name": name, "value": value} for name, value in journal_fields_identifier_tupla if value is not None
                ],
                "fields": [
                    {"name": name, "value": value} for name, value in journal_fields_tupla if value is not None
                ]
            }
            
            # Monta a estrutura que o XMLWriter espera
            new_record = {
                "entities": [new_entity_journal],
                "relations":[]
            }
            
            transformed_records.append(new_record)
        return transformed_records
    
    
    