from xml.dom.minidom import Element
import xml.etree.ElementTree as ET
from typing import List
from validators.orgunit_validator import OrgUnitValidator
from validators.person_validator import PersonValidator
from util.helper_nbr_rene import nbr_title
from validators.base_validator import BaseValidator
from util.unique_identifier_generator import brcrisid_generator
from util.text_transformers import formart_date_str_eng_to_ptbr, trata_string
from .base_mapper import BaseMapper



class PatentBrcris2PatentMapper(BaseMapper):
    def get_source(self) -> str:
        return "Lattes"

    def transform(self, records: ET[Element[str]], validators: List[BaseValidator] = []) -> list[dict]:
        """
        Converte registros de entrada para uma estrutura de dicionário
        pronta para ser convertida em XML pelo XMLWriter.
        """
        if records is None:
            return None
        
        person_validator = self.retrieve_validator_by_type(validators,PersonValidator)
        if person_validator is None:
            raise "PersonValidator not found in validators list"
        
        orgunit_validator = self.retrieve_validator_by_type(validators,OrgUnitValidator)
        if orgunit_validator is None:
            raise "OrgUnitValidator not found in validators list"
        

        root = records.getroot()

       

        new_records = {
                    "entities": [],
                    "relations":[]
                }
        
        transformed_records = []
        ignore_person_dic ={}
        ignore_orgunit_dic ={}

        for entity in root.findall('./entities/entity'):
            # Identificador semanticos 
            patent_SemanticIdentifiers_tupla = []
            # Campos Identificador
            patent_fields_identifier_tupla = []
            # Campos field
            patent_fields_tupla = []
            
            titulo_lattes_brcrisid= None
            titulo_espacenet_brcrisid= None
            ano_deposito_brcrisid= None

            # Cria um dicionário com os atributos básicos (ref, type)
            entidade_dict = entity.attrib.copy()# Itera sobre os filhos diretos da entidade

            if entidade_dict['type'] == 'Patent':
                # Gerando a referência deste registro para relacionamentos
                patent_ref =entidade_dict['ref']
                print(f"Processando registro: {patent_ref}")

                for entity_field_child in entity:
                    # Pegando todos os identificadores semanticos desconsiderando o BrCrisID
                    if entity_field_child.tag == 'semanticIdentifier':
                        valor = entity_field_child.text
                        if valor is not None:
                            if str(valor).startswith('brcris::') == False:
                                patent_SemanticIdentifiers_tupla.append((str(valor).split('::')[0], valor))
                            
                    # Pegando os demais campos da entidade
                    elif entity_field_child.tag == 'field':

                        # Chama a função recursiva para extrair campos e sub-campos
                        entidade_field_dict = self.__processar_field(entity_field_child)
                        
                        if entidade_field_dict is None:
                            continue
                        # <field name="identifier.espacenet" description="Identificação da patente na Expacenet"/>
                        if str(entidade_field_dict['name']).lower() == 'identifier.espacenet':
                            valor_entidade_field_dict = entidade_field_dict['value']
                            if valor_entidade_field_dict is not None:
                                patent_fields_identifier_tupla.append(("identifier.espacenet", valor_entidade_field_dict))

                                patent_SemanticIdentifiers_tupla.append(('espacenet', f"espacenet::{valor_entidade_field_dict}"))

                        # <field name="resourceUrl" description="URL da patente"/>
                        if str(entidade_field_dict['name']).lower() == 'urlespacenet':
                            patent_fields_tupla.append(("resourceUrl", entidade_field_dict['value']))
                        
                        # <field name="kindCode" description="Código de publicação da patente Ex.: A, B1, C1 etc."/>
                        if str(entidade_field_dict['name']).lower() == 'kindcode':
                            patent_fields_tupla.append(("kindCode", entidade_field_dict['value']))

                        # <field name="title" description="Título da patente"/><!-- testar api de padronizacao do Rene?? -->
                        if str(entidade_field_dict['name']).lower() == 'title.espacenet':
                            titulo_espacenet_temp = entidade_field_dict['value']
                            titulo_espacenet_brcrisid = entidade_field_dict['value']
                            if titulo_espacenet_temp is not None:
                                if (titulo_espacenet_brcrisid or "").lower() != (titulo_lattes_brcrisid or "").lower():
                                    titulo_espacenet_temp = nbr_title(titulo_espacenet_temp)
                                    patent_fields_tupla.append(("title", titulo_espacenet_temp))
                        
                        if str(entidade_field_dict['name']).lower() == 'title.lattes':
                            titulo_lattes_temp = entidade_field_dict['value']
                            titulo_lattes_brcrisid = entidade_field_dict['value']
                            if titulo_lattes_temp is not None:
                                if (titulo_espacenet_brcrisid or "").lower() != (titulo_lattes_brcrisid or "").lower():
                                    titulo_lattes_temp = nbr_title(titulo_lattes_temp)
                                    patent_fields_tupla.append(("title", titulo_lattes_temp))

                        # <field name="depositDate" description="Data de depósito da patente"/> <!-- data completa padrao pt-br -->    
                        if str(entidade_field_dict['name']).lower() == 'depositdate':     
                            data_temp, ano =formart_date_str_eng_to_ptbr(entidade_field_dict['value'])        
                            patent_fields_tupla.append(("depositDate", data_temp))

                            if ano is not None:
                                ano_deposito_brcrisid = ano


                        # <field name="publicationDate" description="Data de publicação da patente"/> <!-- data completa padrao pt-br -->
                        if str(entidade_field_dict['name']).lower() == 'publicationdate':     
                            data_temp, ano =formart_date_str_eng_to_ptbr(entidade_field_dict['value'])        
                            patent_fields_tupla.append(("publicationDate", data_temp))

                        # <field name="countryCode" description="Código do país de depósito da patente"/>
                        if str(entidade_field_dict['name']).lower() == 'countrycode':
                            patent_fields_tupla.append(("countryCode", entidade_field_dict['value']))

                        # <field name="inventor" description="Nome do inventor da patente"/>
                        if str(entidade_field_dict['name']).lower() == 'inventor':
                            patent_fields_tupla.append(("inventor", entidade_field_dict['value']))

                        # <field name="applicant"  description="Nome do depositante da patente"/>
                        if str(entidade_field_dict['name']).lower() == 'applicant':
                            patent_fields_tupla.append(("applicant", entidade_field_dict['value']))

                        # <field name="classification.ipc" description="Classificação IPC recebida pela patente">
                        #     <field name="sequence" description="Ordem das classificações"/>
                        #     <field name="text" description="Código completo da classificação"/>
                        #     <field name="section" description="Seção (Parte do código da classificação)"/>
                        #     <field name="class" description="Classe (Parte do código da classificação)"/>
                        #     <field name="subclass"  description="Sub-classe (Parte do código da classificação)"/>
                        #     <field name="group" description="Grupo (Parte do código da classificação)"/>
                        #     <field name="subgroup"  description="Sub-grupo (Parte do código da classificação)"/>
                        # </field>
                        if str(entidade_field_dict['name']).lower() == 'classification.ipc':
                            c_sequence =None
                            c_text =None
                            c_section =None
                            c_class=None
                            c_subclass =None
                            c_group =None
                            c_subgroup =None

                            if 'sub_campos' in entidade_field_dict:
                                for sub_campo in entidade_field_dict['sub_campos']:
                                    if sub_campo['name'] == 'sequence': c_sequence = trata_string(sub_campo['value'])
                                    if sub_campo['name'] == 'text': c_text = sub_campo['value']
                                    if sub_campo['name'] == 'section': c_section = sub_campo['value']
                                    if sub_campo['name'] == 'class': c_class = sub_campo['value']
                                    if sub_campo['name'] == 'subclass': c_subclass = sub_campo['value']
                                    if sub_campo['name'] == 'group': c_group = sub_campo['value']
                                    if sub_campo['name'] == 'subgroup': c_subgroup = sub_campo['value']
                                
                            classificationIpc = {
                                "sequence": c_sequence,
                                "text": c_text,
                                "section": c_section,
                                "class": c_class,
                                "subclass": c_subclass,
                                "group": c_group,
                                "subgroup": c_subgroup  
                            }
                            patent_fields_tupla.append(("classification.ipc", classificationIpc))

                        # <field name="classification.cpc" description="Classificação CPC recebida pela patente">
                        #     <field name="sequence"  description="Ordem das classificações"/>
                        #     <field name="text" description="Código completo da classificação"/>
                        # </field>
                        #TODO 

                        # <field name="abstract"  description="Resumo da patente"/>
                        if str(entidade_field_dict['name']).lower() == 'abstract.espacenet':
                            patent_fields_tupla.append(("abstract", entidade_field_dict['value']))

                        # <field name="originatesFrom" description="Código da Família da patente, conforme organização definida pela Espacenet"/>
                        if str(entidade_field_dict['name']).lower() == 'originatesFrom':
                            patent_fields_tupla.append(("originatesFrom", trata_string(entidade_field_dict['value'])))

                        # <field name="alternateIdentifier" description="Códigos alternativos de identificação da Patente">
                        #     <field name="status"  description="Status do número de identificação"/>
                        #     <field name="format" description="Formato atribuído a numeração, conforme padrão da Espacenet"/>
                        #     <field name="country" description="País de depósito da patente"/>
                        #     <field name="number" description="Número de identificação da patente "/>
                        #     <field name="kind" description="Código de publicação da patente Ex.: A, B1, C1 etc."/>
                        # </field>
                        if str(entidade_field_dict['name']).lower() == 'alternateidentifier':
                            c_status =None
                            c_format =None
                            c_country =None
                            c_number=None
                            c_kind =None

                            if 'sub_campos' in entidade_field_dict:
                                for sub_campo in entidade_field_dict['sub_campos']:
                                    if sub_campo['name'] == 'status': c_status = sub_campo['value']
                                    if sub_campo['name'] == 'format': c_format = sub_campo['value']
                                    if sub_campo['name'] == 'country': c_country = sub_campo['value']
                                    if sub_campo['name'] == 'number': c_number = sub_campo['value']
                                    if sub_campo['name'] == 'kind': c_kind = sub_campo['value']
                                
                            alternateIdentifier = {
                                "status": c_status,
                                "format": c_format,
                                "country": c_country,
                                "number": c_number,
                                "kind": c_kind
                            }
                            patent_fields_tupla.append(("alternateIdentifier", alternateIdentifier))

                # Gerar o BRCRISID     
                brcris_id_v1_1 = None
                brcris_id_v1_2 = None 
                if titulo_lattes_brcrisid and ano_deposito_brcrisid:
                    brcris_id_v1_1 = brcrisid_generator(titulo_lattes_brcrisid,ano_deposito_brcrisid)
                    patent_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1_1}"))
                if titulo_espacenet_brcrisid and ano_deposito_brcrisid:
                    brcris_id_v1_2 = brcrisid_generator(titulo_espacenet_brcrisid,ano_deposito_brcrisid)
                    if brcris_id_v1_2 != brcris_id_v1_1:
                        patent_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1_2}"))

                brcris_id_v2_1 = None
                brcris_id_v2_2 = None 
                if titulo_lattes_brcrisid and ano_deposito_brcrisid:
                    brcris_id_v2_1 = brcrisid_generator(titulo_lattes_brcrisid,ano_deposito_brcrisid,useReplaceHtmlChars=True)
                    if brcris_id_v2_1 != brcris_id_v1_1:
                        patent_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v2_1}"))
                if titulo_espacenet_brcrisid and ano_deposito_brcrisid:
                    brcris_id_v2_2 = brcrisid_generator(titulo_espacenet_brcrisid,ano_deposito_brcrisid,useReplaceHtmlChars=True)
                    if brcris_id_v2_2 != brcris_id_v2_1 and brcris_id_v2_2 != brcris_id_v1_2:
                        patent_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v2_2}"))
                
                # Monta a estrutura que o XMLWriter espera
                new_entity_patenty = {
                    "entity_attribs": {
                        "type": "Patent",
                        "ref": patent_ref
                    },
                    "semantic_identifiers":[
                        {"name": name, "value": value} for name, value in patent_SemanticIdentifiers_tupla if value is not None
                    ],
                    "fields_identifier": [
                        {"name": name, "value": value} for name, value in patent_fields_identifier_tupla if value is not None
                    ],
                    "fields": [
                        {"name": name, "value": value} for name, value in patent_fields_tupla if value is not None
                    ]
                }

                new_records["entities"].append(new_entity_patenty)
            
            if entidade_dict['type'] == 'Person':
                person_ref = entidade_dict['ref']
                print(f"Processando registro: {person_ref}")

                person_fields_identifier_tupla = []
                person_SemanticIdentifiers_tupla = []

                for entity_field_person_child in entity:

                    if entity_field_person_child.tag == 'field':
                        entidade_person_field_dict = self.__processar_field(entity_field_person_child)

                        if str(entidade_person_field_dict['name']).lower() == 'identifier.lattes':

                            id_alttes = entidade_person_field_dict['value']
                            id_alttes = str(id_alttes).zfill(16)

                            if person_validator.is_valid(id_alttes):
                                person_fields_identifier_tupla.append(("identifier.lattes", id_alttes))
                                person_SemanticIdentifiers_tupla.append(("brcris", f"lattes::{id_alttes}"))

                                new_entity_person = {
                                    "entity_attribs": {
                                        "type": "Person",
                                        "ref": person_ref
                                    },
                                    "semantic_identifiers":[
                                        {"name": name, "value": value} for name, value in person_SemanticIdentifiers_tupla if value is not None
                                    ],
                                    "fields_identifier": [
                                        {"name": name, "value": value} for name, value in person_fields_identifier_tupla if value is not None
                                    ],
                                    "fields": []
                                }

                                new_records["entities"].append(new_entity_person)
                            else:
                               ignore_person_dic[person_ref]= True

            if entidade_dict['type'] == 'OrgUnit':
                orgunit_ref = entidade_dict['ref']
                print(f"Processando registro: {orgunit_ref}")

                orgunit_SemanticIdentifiers_tupla = []

                for entity_field_orgunit_child in entity:
                    if entity_field_orgunit_child.tag == 'field':
                        entidade_orgunit_field_dict = self.__processar_field(entity_field_orgunit_child)

                        if str(entidade_orgunit_field_dict['name']).lower() == 'name':

                            orgunit_name = entidade_orgunit_field_dict['value']

                            orgunit_is_valid, key_orgunit = orgunit_validator.is_valid(orgunit_name)
            
                            if orgunit_is_valid == True:
                                orgunit_brcris_id_v1 = brcrisid_generator(key_orgunit)
                                orgunit_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{orgunit_brcris_id_v1}"))
                                orgunit_brcris_id_v2 = brcrisid_generator(key_orgunit,useReplaceHtmlChars=True)
                                if orgunit_brcris_id_v1 != orgunit_brcris_id_v2:
                                    orgunit_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{orgunit_brcris_id_v2}v2"))


                                new_entity_orgunit = {
                                    "entity_attribs": {
                                        "type": "OrgUnit",
                                        "ref": orgunit_ref
                                    },
                                    "semantic_identifiers":[
                                        {"name": name, "value": value} for name, value in orgunit_SemanticIdentifiers_tupla if value is not None
                                    ],
                                    "fields_identifier": [],
                                    "fields": []
                                }

                                new_records["entities"].append(new_entity_orgunit)
                            else:
                               ignore_orgunit_dic[orgunit_ref]= True


        for relation in root.findall('./relations/relation'):        

            relation_dict = relation.attrib.copy()
            # <relation name="Inventor" description="Is a relation related to an Person of Patent." fromEntity="Patent" toEntity="Person"/>
            if relation_dict['type'] == 'Inventor':
                toEntityRef = relation_dict['toEntityRef']
                if toEntityRef in ignore_person_dic:
                    continue

                new_relation = {
                    "type": "Inventor",
                    "fromEntityRef": relation_dict['fromEntityRef'], # fromEntity="Patent"
                    "toEntityRef":  relation_dict['toEntityRef'] # toEntity="Person"
                } 
            
                new_records["relations"].append(new_relation)
            # <relation name="Applicant" description="Is a relation related to an OrgUnit of Patent." fromEntity="Patent" toEntity="OrgUnit"/>
            elif relation_dict['type'] == 'Applicant':
                toEntityRef = relation_dict['toEntityRef']
                if toEntityRef in ignore_orgunit_dic:
                    continue

                new_relation = {
                    "type": "Applicant",
                    "fromEntityRef": relation_dict['fromEntityRef'], # fromEntity="Patent"
                    "toEntityRef":  relation_dict['toEntityRef'] # toEntity="OrgUnit"
                } 
            
                new_records["relations"].append(new_relation)
            else:
                print(relation_dict['type'])
            
            
            
        transformed_records.append(new_records)
        return transformed_records
    
    # processar campos que podem ter sub-campos (Recursividade)
    def __processar_field(self, field_element):
        # Pega os atributos do campo atual (ex: name, value)
        dados_field = field_element.attrib.copy()
        
        # Verifica se este campo tem filhos (sub-campos)
        sub_campos = list(field_element)
        if sub_campos:
            dados_field['sub_campos'] = [self.__processar_field(child) for child in sub_campos]
            
        return dados_field