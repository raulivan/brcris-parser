from logging import Logger
from typing import List, Optional
from validators.orgunit_validator import OrgUnitValidator
from validators.person_validator import PersonValidator
from validators.base_validator import BaseValidator
from util.unique_identifier_generator import brcrisid_generator
from util.text_transformers import capitalizar_nome, trata_string
from .base_mapper import BaseMapper
import hashlib
import xml.etree.ElementTree as ET

class RelacionamentoGrupoPesquisaMapper(BaseMapper):
    def get_source(self) -> str:
        return "Lattes"

    def transform(self, records: list[dict], logger:Logger, validators: List[BaseValidator] = []) -> list[dict]:
        """
        Converte registros  de entrada para uma estrutura de dicionário
        pronta para ser convertida em XML pelo XMLWriter.
        """

        person_validator = self.retrieve_validator_by_type(validators,PersonValidator)
        if person_validator is None:
            raise "PersonValidator not found in validators list"
        
        orgunit_validator = self.retrieve_validator_by_type(validators,OrgUnitValidator)
        if orgunit_validator is None:
            raise "OrgUnitValidator not found in validators list"

        if records is None:
            return None
        
        transformed_records = []
        
        for record in records:
            
            root = ET.fromstring(record)


            namespaces = {'ns': 'http://www.cnpq.br/lmpl/2002/XSD/Grupo'}
            
            # Identificador semanticos 
            group_SemanticIdentifiers_tupla = []
            # Campos Identificador
            group_fields_identifier_tupla = []
            # Campos field
            group_fields_tupla = []
            

            # Recuperando informações de identificação do grupo de pesquisa
            ano_cricao = None
            nome_grupo = None
            id_grupo = root.attrib.get('NRO-ID-GRUPO')
            if (id_grupo is None) or (str(id_grupo).strip() == ""):
                continue
            
            # Gerando a referência deste registro para relacionamentos
            grupo_ref = self.creat_ref_identifier()

            group_SemanticIdentifiers_tupla.append(("brcris", f"dgp::{id_grupo}"))
            group_fields_identifier_tupla.append(("identifier.dgp", id_grupo))

            # tagIdentificacao =  tree.find('.//ns:IDENTIFICACAO-DO-GRUPO', namespaces)
            # if tagIdentificacao != None:
            #     ano_criacao = tagIdentificacao.attrib.get('ANO-DE-CRIACAO')
            #     nome_grupo = tagIdentificacao.attrib.get('NOME-DO-GRUPO')

            
            new_entity_group = {
                "entity_attribs": {
                    "type": "ResearchGroup",
                    "ref": grupo_ref
                },
                "semantic_identifiers":[
                    {"name": name, "value": value} for name, value in group_SemanticIdentifiers_tupla if value is not None
                ],
                "fields_identifier": [
                    {"name": name, "value": value} for name, value in group_fields_identifier_tupla if value is not None
                ],
                "fields": [
                    {"name": name, "value": value} for name, value in group_fields_tupla if value is not None
                ]
            }
            
            # Monta a estrutura que o XMLWriter espera
            new_record = {
                "entities": [new_entity_group],
                "relations":[]
            }
            
            # ****************** Montando as entidades de relacionamento com a entidade principal gerada ********************
            # 01 - Lideres do grupo
            tag_lideres = root.find('.//ns:LIDERES', namespaces)

            if tag_lideres is not None:
                for lider in tag_lideres:
                    new_person, person_ref, nro_id_cnpq, cargo = self.__transform_person(lider)
                    if not new_person is None:
                        if person_validator.is_valid(nro_id_cnpq):
                            new_relation = {
                                "type": "LeaderResearchGroup",
                                "fromEntityRef": person_ref, # fromEntity="Person"
                                "toEntityRef":  grupo_ref, # toEntity="ResearchGroup"
                            } 
                            new_record["relations"].append(new_relation)
                            new_record["entities"].append(new_person)
                    

            # 02 - Pesquisadores membros do grupos
            tag_pesquisadores = root.find('.//ns:PESQUISADORES', namespaces)

            if tag_pesquisadores is not None:
                for pesquisador in tag_pesquisadores:
                    new_person, person_ref, nro_id_cnpq, cargo = self.__transform_person(pesquisador)
                    if not new_person is None:
                        if person_validator.is_valid(nro_id_cnpq):
                            new_relation = {
                                "type": "MemberResearchGroup",
                                "fromEntityRef": person_ref, # fromEntity="Person"
                                "toEntityRef":  grupo_ref, # toEntity="ResearchGroup"
                                "attributes":[
                                {"name": "role", "value": cargo} if cargo is not None else None
                            ]
                            } 
                            new_record["relations"].append(new_relation)
                            new_record["entities"].append(new_person)

            # 03 - Estudantes membros do grupos
            tag_estudantes = root.find('.//ns:ESTUDANTES', namespaces)

            if tag_estudantes is not None:
                for estudante in tag_estudantes:
                    new_person, person_ref, nro_id_cnpq, cargo = self.__transform_person(estudante)
                    if not new_person is None:
                        if person_validator.is_valid(nro_id_cnpq):
                            new_relation = {
                                "type": "MemberResearchGroup",
                                "fromEntityRef": person_ref, # fromEntity="Person"
                                "toEntityRef":  grupo_ref, # toEntity="ResearchGroup"
                                "attributes":[
                                {"name": "scholarshipHolder", "value": "True"}
                            ]
                            } 
                            new_record["relations"].append(new_relation)
                            new_record["entities"].append(new_person)


            # 03 - Estudantes Orgunits parte dp grupo
            tag_empresas = root.find('.//ns:EMPRESAS', namespaces)

            if tag_empresas is not None:
                for empresa in tag_empresas:
                    new_orgunit, orgunit_ref = self.__transform_orgunit(empresa, orgunit_validator)
                    if not new_orgunit is None:
                        new_relation = {
                            "type": "PartnerResearchGroupOrgUnit",
                            "fromEntityRef": orgunit_ref, # fromEntity="OrgUnit"
                            "toEntityRef":  grupo_ref, # toEntity="ResearchGroup"
                        } 
                        new_record["relations"].append(new_relation)
                        new_record["entities"].append(new_orgunit)
        
            
            

            
            transformed_records.append(new_record)
        return transformed_records
    
    def __transform_person(self, tag_pessoa:ET[str]) -> tuple[dict, str]:
        """
        Converte registros  de autores  
        """
       
        author_SemanticIdentifiers_tupla = []
        author_fields_identifier_tupla = []
        author_fields_tupla = []

        # Extrai o valor do atributo NRO-ID-CNPQ
        nro_id_cnpq = tag_pessoa.attrib.get('NRO-ID-CNPQ')
        nome_da_tag = tag_pessoa.tag.split('}')[-1]
        if 'LIDER' in str(nome_da_tag):
            nome_da_tag = 'Líder'
        else:
            nome_da_tag = None


        author_SemanticIdentifiers_tupla.append(("lattes", f"lattes::{nro_id_cnpq}"))

        # Gerando a referência deste registro para relacionamentos
        author_ref = self.creat_ref_identifier()

       
        new_entity_person= {
            "entity_attribs": {
                "type": "Person",
                "ref": author_ref
            },
            "semantic_identifiers":[
                {"name": name, "value": value} for name, value in author_SemanticIdentifiers_tupla if value is not None
            ],
            "fields_identifier": [
                {"name": name, "value": value} for name, value in author_fields_identifier_tupla if value is not None
            ],
            "fields": [
                {"name": name, "value": value} for name, value in author_fields_tupla if value is not None
            ]
        }
        
        if len(author_SemanticIdentifiers_tupla) == 0:
            return None, None, None, None
        
        
        return new_entity_person, author_ref, nro_id_cnpq, nome_da_tag
    
    def __transform_orgunit(self, orgunit_dict:ET[str], validator:OrgUnitValidator) -> tuple[dict, str]:
        
        
        orgunit_SemanticIdentifiers_tupla = []
        orgunit_fields_identifier_tupla = []
        orgunit_fields_tupla = []
        
        nome_instituicao = orgunit_dict.attrib.get('NOME-DA-EMPRESA')
        razao_social_instituicao = orgunit_dict.attrib.get('RAZAO-SOCIAL-DA-EMPRESA')
        
        if nome_instituicao is None and razao_social_instituicao is None:
            return None, None
        
        orgunit_is_valid =False
        key_orgunit = None

        if trata_string(nome_instituicao):
            orgunit_is_valid, key_orgunit = validator.is_valid(nome_instituicao)
            
        if not orgunit_is_valid:
            if trata_string(razao_social_instituicao):
                orgunit_is_valid, key_orgunit = validator.is_valid(razao_social_instituicao)
       
        if orgunit_is_valid == False:
            return None, None
        
        # <field name="identifier.brcris" description="MD5 do id devolvido pela API do Rene"/>
        orgunit_brcris_id_v1 = brcrisid_generator(key_orgunit)
        orgunit_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{orgunit_brcris_id_v1}"))

        orgunit_brcris_id_v2 = brcrisid_generator(key_orgunit,useReplaceHtmlChars=True)
        if orgunit_brcris_id_v1 != orgunit_brcris_id_v2:
            orgunit_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{orgunit_brcris_id_v2}v2"))
        
        # Gerando a referência deste registro para relacionamentos
        orgunit_ref = self.creat_ref_identifier()

       
        new_entity_orgunit= {
            "entity_attribs": {
                "type": "OrgUnit",
                "ref": orgunit_ref
            },
            "semantic_identifiers":[
                {"name": name, "value": value} for name, value in orgunit_SemanticIdentifiers_tupla if value is not None
            ],
            "fields_identifier": [
                {"name": name, "value": value} for name, value in orgunit_fields_identifier_tupla if value is not None
            ],
            "fields": [
                {"name": name, "value": value} for name, value in orgunit_fields_tupla if value is not None
            ]
        }
        
        
        return new_entity_orgunit, orgunit_ref
    
    
    
       