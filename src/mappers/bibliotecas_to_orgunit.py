from logging import Logger
from typing import List
from validators.orgunit_validator import OrgUnitValidator
from util.text_validator import validar_titulo
from util.helper_nbr_rene import nbr_title
from validators.base_validator import BaseValidator
from util.unique_identifier_generator import brcrisid_generator
from util.text_transformers import trata_string
from .base_mapper import BaseMapper


class BibliotecasOrgunitMapper(BaseMapper):
    def get_source(self) -> str:
        return "IBICT"

    def transform(self, records: list[dict], logger:Logger, validators: List[BaseValidator] = [], relaciona_dono_curriculo: bool = True, relaciona_coautor:bool = True) -> list[dict]:
        """
        Converte registros de entrada para uma estrutura de dicionário
        pronta para ser convertida em XML pelo XMLWriter.
        """
        if records is None:
            return None

        
        orgunit_validator = self.retrieve_validator_by_type(validators,OrgUnitValidator)
        if orgunit_validator is None:
            raise "OrgUnitValidator not found in validators list"
            
        
        # Relacionamento com cursos
        transformed_records = []
        eh_header = True

        
        sigla_idx = 0
        nome_idx = 1
        departamento_unidade_idx =2
        biblioteca_idx = 3
        endereco_idx = 4
        cidade_idx = 5
        uf_idx = 6
        r_idx = 7
        cep_idx = 8
        

        for record_item in records:
            if (record_item == None) or (record_item == "") or (len(record_item) == 0):
                continue
            
            if eh_header:
                eh_header = False
                
                idx = 0
                for coluna in record_item:
                    if coluna == 'SIGLA':
                        sigla_idx = idx
                    elif coluna == 'NOME': # nome da orgunit dona
                        nome_idx = idx
                    elif coluna == 'DEPARTAMENTO' or coluna == 'UNIDADE':
                        departamento_unidade_idx = idx
                    elif coluna == 'BIBLIOTECA':
                        biblioteca_idx = idx
                    elif coluna == 'ENDEREÇO':
                        endereco_idx = idx
                    elif coluna == 'CIDADE':
                        cidade_idx = idx
                    elif coluna == 'UF':
                        uf_idx = idx
                    elif coluna == 'R' or coluna == 'REG':
                        r_idx = idx
                    elif coluna == 'CEP':
                        cep_idx = idx
                    
                    idx = idx + 1

                continue
            
                        
            # Identificador semanticos 
            orgunit_SemanticIdentifiers_tupla = []
            # Campos Identificador
            orgunit_fields_identifier_tupla = []
            # Campos field
            orgunit_fields_tupla = []
            

            # Verificando se a ORgunit dona da biblioteca é válida
            orgunit_owner = self.get_csv_field_value(record_item, nome_idx)
            orgunit_owner_is_valid, key_orgunit_owner = orgunit_validator.is_valid(orgunit_owner)
            if orgunit_owner_is_valid == False:
                # Não é uma orgunit válida e vai pro próximo
                continue
            
            # Gerando a referência deste registro para relacionamentos
            orgunit_ref = self.creat_ref_identifier()

            print(f"Processando registro: {orgunit_ref}")

            # <field name="identifier.brcris" description="MD5 do id devolvido pela API do Rene"/>
            instituicao_nome = self.get_csv_field_value(record_item, nome_idx)
            biblioteca_nome = self.get_csv_field_value(record_item, biblioteca_idx)

            if validar_titulo(instituicao_nome) == False:
                continue
            if validar_titulo(biblioteca_nome) == False:
                continue           

            brcris_id_v1 = brcrisid_generator(instituicao_nome,biblioteca_nome)
            brcris_id_v2 = brcrisid_generator(instituicao_nome,biblioteca_nome,useReplaceHtmlChars=True)

            orgunit_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}"))
            orgunit_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
            if brcris_id_v1 != brcris_id_v2:
                orgunit_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v2}v2"))
                orgunit_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v2}v2"))
    
            # <field name="type"/>
            orgunit_fields_identifier_tupla.append(("type", "Biblioteca"))

            # <field name="juridicNature" description="Natureza Organizacional"/>
            # TODO

            # <field name="acronym" description="Sigla da organização"/>
            # TODO


            # <field name="name" description="nome da organização"/>
            orgunit_nome = self.get_csv_field_value(record_item, biblioteca_idx)
            if self.has_value(orgunit_nome):
                orgunit_nome = nbr_title(orgunit_nome)
                orgunit_fields_tupla.append(("name", orgunit_nome))

            # <field name="electronicAddress"/>
            # TODO

            # <field name="latitude"/>

            # <field name="longitude"/>
            # TODO

            # <field name="address"/>
            orgunit_address = self.get_csv_field_value(record_item, endereco_idx)
            if self.has_value(orgunit_address):
                orgunit_address = nbr_title(orgunit_address)
                orgunit_fields_tupla.append(("address", orgunit_address))

            # <field name="cep"/>
            orgunit_cep = self.get_csv_field_value(record_item, cep_idx)
            if self.has_value(orgunit_cep):
                orgunit_cep = nbr_title(orgunit_cep)
                orgunit_fields_tupla.append(("cep", orgunit_cep))
        

            # <field name="city"/><!-- validar na lista de autoridade de cidades se o país for Brasil -->
            orgunit_city = self.get_csv_field_value(record_item, cidade_idx)
            if self.has_value(orgunit_city):
                orgunit_city = nbr_title(orgunit_city)
                orgunit_fields_tupla.append(("city", orgunit_city))

            # <field name="neighborhood"/>
            # TODO

            # <field name="state"/><!-- validar na lista de autoridade de estados se o país for Brasil -->
            orgunit_state = self.get_csv_field_value(record_item, uf_idx)
            if self.has_value(orgunit_state):
                orgunit_state = nbr_title(orgunit_state)
                orgunit_fields_tupla.append(("state", orgunit_state))

            # <field name="country"/> <!-- validar na lista de autoridade de país -->
            orgunit_fields_tupla.append(("country", "Brasil"))

            # <field name="phone"/>
            # TODO

            # <field name="websiteUrl" description="Site da organização"/> <!-- checar se é uma url -->
            # TODO

            # Monta a estrutura que o XMLWriter espera
            new_entity_research_group = {
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

            new_record = {
                "entities": [new_entity_research_group],
                "relations":[]
            }

            # Unidade da biblioteca
            # <relation name="IsUnitOf" description="The unit related to an organization." fromEntity="OrgUnit" toEntity="OrgUnit"/>
            new_orgunit_owner, orgunit_ref_owner = self.__transform_orgunit(orgunit_owner, orgunit_validator)
            if not new_orgunit_owner is None:
                new_relation = {
                    "type": "IsUnitOf",
                    "fromEntityRef": orgunit_ref_owner , # fromEntity="OrgUnit"
                    "toEntityRef":  orgunit_ref, # toEntity="OrgUnit"
                } 
                new_record["relations"].append(new_relation)
                new_record["entities"].append(new_orgunit_owner)
            
            transformed_records.append(new_record)
        return transformed_records

    
    
    def __transform_orgunit(self, orgunit:str, validator:OrgUnitValidator) -> tuple[dict, str]:
        
        
        orgunit_SemanticIdentifiers_tupla = []
        orgunit_fields_identifier_tupla = []
        orgunit_fields_tupla = []
        
        
        if orgunit is None:
            return None, None
        
        orgunit_is_valid =False
        key_orgunit = None

        if trata_string(orgunit):
            orgunit_is_valid, key_orgunit = validator.is_valid(orgunit)
       
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
    
           