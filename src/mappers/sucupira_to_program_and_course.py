from typing import List, Optional
from validators.orgunit_validator import OrgUnitValidator
from validators.base_validator import BaseValidator
from util.unique_identifier_generator import brcrisid_generator
from util.text_transformers import capitalizar_nome, trata_string
from .base_mapper import BaseMapper
import hashlib


class Sucupira2ProgramAndCourseMapper(BaseMapper):
    def get_source(self) -> str:
        return "Sucupira"

    def transform(self, records: list[dict], validators: List[BaseValidator] = []) -> list[dict]:
        """
        Converte registros  de entrada para uma estrutura de dicionário
        pronta para ser convertida em XML pelo XMLWriter.
        """
        if records is None:
            return None
        
        transformed_records = []
        
        records_loop = records if records is List else [records]
        for record in records_loop:
            
            # Identificador semanticos 
            program_SemanticIdentifiers_tupla = []
            # Campos Identificador
            program_fields_identifier_tupla = []
            # Campos field
            program_fields_tupla = []
            
            # Recuperando um subgrupo com informações importantes
            record_tag_online = self.get_field_value(record, "online")
            
            # Recupera a listagem de instituições
            record_tag_online_instituicoes = self.get_field_value(record_tag_online, "instituicoes")
             
            # Gerando a referência deste registro para relacionamentos
            program_ref = self.creat_ref_identifier()
             
            # # Recupera a modalidade para usar na hora de montar os cursos
            # program_course_modalidade= self.get_field_value(record, "modalidade")
            
           
            # <field name="name" description="Program Name"/>
            program_name_temp = self.get_field_value(record, "nome")
            if program_name_temp is not None:
                program_name_temp = capitalizar_nome(program_name_temp)
                program_fields_tupla.append(("name", program_name_temp))
                
            
            # <field name="researchArea.capes" description="capes vocabulary"/>
            #           Grande Area / Area / Sub-area / Especialidade
            grande_area = self.get_field_value(record, "nomeGrandeAreaConhecimento")
            area = self.get_field_value(record, "nomeAreaConhecimento")
            program_fields_tupla.append(("researchArea.capes", f"{grande_area} / {area}"))

            
            # <field name="researchArea.cnpq" description="cnpq vocabulary"/> 
            # NÃO SE APLICA
            
            # <field name="evaluationArea" description="cnpq vocabulary"/>
            area_avaliacao = self.get_field_value(record, "nomeAreaAvaliacao")
            program_fields_tupla.append(("evaluationArea", trata_string(area_avaliacao)))
            
            # <field name="phone"/>
            program_phone_ddd = self.get_field_value(record_tag_online, "telDdd")
            program_phone = self.get_field_value(record_tag_online, "telNumero")
            program_phone =f"({trata_string(program_phone_ddd)}) {trata_string(program_phone)}"
            program_fields_tupla.append(("phone", trata_string(program_phone)))
            
            # <field name="email"/>
            program_email = self.get_field_value(record_tag_online, "contatoEmail")
            program_fields_tupla.append(("email", trata_string(program_email)))
            
            # <field name="websiteUrl"/>
            program_websiteUrl = self.get_field_value(record_tag_online, "contatoUrl")
            program_fields_tupla.append(("websiteUrl", trata_string(program_websiteUrl)))

            # Gerando o BRCRISID
            
            if not record_tag_online_instituicoes is None:            
                primeira_instituicao = record_tag_online_instituicoes[0]
                if primeira_instituicao is not None:
                    nome_instituicao = self.get_field_value(primeira_instituicao, "nomeIes")
                    if nome_instituicao is not None:
                        program_brcris_id_v1 = brcrisid_generator(program_name_temp,trata_string(nome_instituicao))
                        program_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{program_brcris_id_v1}"))
                        program_fields_identifier_tupla.append(("identifier.brcris", program_brcris_id_v1))
                        program_brcris_id_v2 = brcrisid_generator(program_name_temp,trata_string(nome_instituicao),useReplaceHtmlChars=True)
                        if program_brcris_id_v1 != program_brcris_id_v2:
                            program_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{program_brcris_id_v2}v2"))
                            program_fields_identifier_tupla.append(("identifier.brcris", f"{program_brcris_id_v2}v2"))

            
            program_codigo = self.get_field_value(record_tag_online, "codigo")
            program_SemanticIdentifiers_tupla.append(("capes", f"capes::{trata_string(program_codigo)}"))
            program_fields_identifier_tupla.append(("identifier.capes", trata_string(program_codigo)))

            if len(program_SemanticIdentifiers_tupla) == 0:
                continue
            
            new_entity_program = {
                "entity_attribs": {
                    "type": "Program",
                    "ref": program_ref
                },
                "semantic_identifiers":[
                    {"name": name, "value": value} for name, value in program_SemanticIdentifiers_tupla if value is not None
                ],
                "fields_identifier": [
                    {"name": name, "value": value} for name, value in program_fields_identifier_tupla if value is not None
                ],
                "fields": [
                    {"name": name, "value": value} for name, value in program_fields_tupla if value is not None
                ]
            }
            
            # Monta a estrutura que o XMLWriter espera
            new_record = {
                "entities": [new_entity_program],
                "relations":[]
            }
            
            # ****************** Montando as entidades de relacionamento com a entidade principal gerada ********************
            # 01 - OrgUnit
            orgunit_validator = self.retrieve_validator_by_type(validators,OrgUnitValidator)
            for instituicoes_item in record_tag_online_instituicoes:
                if instituicoes_item is not None:
                    new_orgunit, orgunit_ref = self.__transform_orgunit(instituicoes_item, orgunit_validator)
                    
                    if new_orgunit is None:
                        continue
                    
                    new_relation = {
                        "type": "OrgUnitProgram",
                        "fromEntityRef": orgunit_ref, # fromEntity="OrgUnit"
                        "toEntityRef": program_ref  # toEntity="Program"
                    } 
                    
                    new_record["relations"].append(new_relation)
                    new_record["entities"].append(new_orgunit)
            
            
            # 02 - Cursos
            primeira_instituicao = record_tag_online_instituicoes[0]
            program_course_modalidade = self.get_field_value(record, "modalidade")
            record_tag_cursos = self.get_field_value(record_tag_online, "cursos")
            if record_tag_cursos is not None:
                for curso in record_tag_cursos:
                    if curso is not None:
                        new_course, course_ref = self.__transform_course(curso, program_course_modalidade, primeira_instituicao)
                        if new_course is None:
                            continue
                        
                        new_relation = {
                            "type": "IsProgramOf",
                            "fromEntityRef": program_ref, # fromEntity="Program"
                            "toEntityRef":  course_ref # toEntity="Course"
                        } 
                        
                        new_record["relations"].append(new_relation)
                        new_record["entities"].append(new_course)

            
            transformed_records.append(new_record)
        return transformed_records
    
    def __transform_orgunit(self, orgunit_dict: dict, validator: OrgUnitValidator = None) -> tuple[dict, str]:
        """
        Converte registros  de cursos  
        """
        if validator is None:
            return None, None
        
        orgunit_SemanticIdentifiers_tupla = []
        orgunit_fields_identifier_tupla = []
        orgunit_fields_tupla = []
        
        
        nome_instituicao = self.get_field_value(orgunit_dict, "nomeIes")
        
        if nome_instituicao is None:
            return None, None
        
        if trata_string(nome_instituicao) == "":
            return None, None
        
        orgunit_is_valid, key_orgunit = validator.is_valid(nome_instituicao)
            
        if not orgunit_is_valid:
            return None, None
        
        # <field name="identifier.brcris" description="MD5 do id devolvido pela API do Rene"/>
        orgunit_brcris_id_v1 = brcrisid_generator(key_orgunit)
        orgunit_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{orgunit_brcris_id_v1}"))
        # orgunit_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
        orgunit_brcris_id_v2 = brcrisid_generator(key_orgunit,useReplaceHtmlChars=True)
        if orgunit_brcris_id_v1 != orgunit_brcris_id_v2:
            orgunit_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{orgunit_brcris_id_v2}v2"))
            # orgunit_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v2}v2"))	
        
        # # <field name="identifier.capes"/>
        # idIes = self.get_field_value(orgunit_dict, "idIes")
        # orgunit_fields_identifier_tupla.append(("identifier.capes", trata_string(idIes)))
        
        # # <field name="acronym" description="Sigla da organização"/>
        # acronym = self.get_field_value(orgunit_dict, "siglaIes")
        # orgunit_fields_tupla.append(("siglaIes", trata_string(acronym)))
        
        # # <field name="name" description="nome da organização"/>
        # nome_instituicao = capitalizar_nome(nome_instituicao)
        # orgunit_fields_tupla.append(("name", trata_string(nome_instituicao)))	
        
        # # <field name="electronicAddress"/>
        # electronicAddress = self.get_field_value(orgunit_dict, "contatoEmail")
        # orgunit_fields_tupla.append(("electronicAddress", trata_string(electronicAddress)))

        # # <field name="state"/><!-- validar na lista de autoridade de estados se o país for Brasil -->
        # state = self.get_field_value(orgunit_dict, "siglaUf")
        # orgunit_fields_tupla.append(("state", trata_string(state)))
        
        # # <field name="websiteUrl" description="Site da organização"/> <!-- checar se é uma url -->
        # websiteUrl = self.get_field_value(orgunit_dict, "contatoUrl")
        # orgunit_fields_tupla.append(("websiteUrl", trata_string(websiteUrl)))
		
        
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
        
        if len(orgunit_SemanticIdentifiers_tupla) == 0:
            return None, None
        
        
        return new_entity_orgunit, orgunit_ref
    
    def __transform_course(self, course: dict, modalidade: str, orgunit_dict: dict) -> tuple[dict, str]:
        """
        Converte registros  de cursos  
        """
        course_SemanticIdentifiers_tupla = []
        course_fields_identifier_tupla = []
        course_fields_tupla = []
        
        # Gerando a referência deste registro para relacionamentos
        course_ref = self.creat_ref_identifier()

        # <field name="name"/>
        course_name = self.get_field_value(course, "nome")
        if course_name == None:
            return None
        
        course_name = capitalizar_nome(course_name)
        course_fields_tupla.append(("name", course_name))
        
        # <field name="degree" description="gradutation, specialization, master, doctoral, posDoctoral, fullProfessor"/><!-- validar na lista de autoridade de graus e gravar no idima PT -->
        course_degree = self.get_field_value(course, "grau")
        course_fields_tupla.append(("degree", trata_string(course_degree)))
        
        # <field name="type" description="Academic/Professional"/> <!-- validar na lista de autoridade de tipo (Academico ou Profissional) e gravar no idima PT -->
        course_type = capitalizar_nome(modalidade)
        course_fields_tupla.append(("type", course_type))
        
        # <field name="startDate"/> <!-- somente ano -->
        course_startDate = self.get_field_value(course, "dataInicio")
        if course_startDate is not None:
            course_startDate = course_startDate.split('-')[0]
            course_fields_tupla.append(("startDate", course_startDate))
            
        # <field name="endDate"/> <!-- somente ano -->
        # NÃO TEM NA FONTE    
        
        # <field name="identifier.brcris"/>
        if not orgunit_dict is None:
            if orgunit_dict is not None:
                nome_instituicao = self.get_field_value(orgunit_dict, "nomeIes")
                if nome_instituicao is not None:
                    course_brcris_id_v1 = brcrisid_generator(course_name,nome_instituicao, course_degree)
                    course_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{course_brcris_id_v1}"))
                    course_fields_identifier_tupla.append(("identifier.brcris", course_brcris_id_v1))
            
                    course_brcris_id_v2 = brcrisid_generator(course_name,nome_instituicao, course_degree,useReplaceHtmlChars=True)
                    if course_brcris_id_v1 != course_brcris_id_v2:
                        course_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{course_brcris_id_v2}"))
                        course_fields_identifier_tupla.append(("identifier.brcris", f"{course_brcris_id_v2}v2"))
                                
        # <field name="identifier.capes"/>    
        codigo = self.get_field_value(course, "codigo")
        course_SemanticIdentifiers_tupla.append(("capes",f"capes::{codigo}"))
        course_fields_identifier_tupla.append(("identifier.capes", codigo))
        # <field name="identifier.mec"/>   
        # <field name="identifier.inep"/>     
        # <field name="identifier.cnpq"/>  
        # <field name="identifier.other"/>     


        
        new_entity_course= {
            "entity_attribs": {
                "type": "Course",
                "ref": course_ref
            },
            "semantic_identifiers":[
                {"name": name, "value": value} for name, value in course_SemanticIdentifiers_tupla if value is not None
            ],
            "fields_identifier": [
                {"name": name, "value": value} for name, value in course_fields_identifier_tupla if value is not None
            ],
            "fields": [
                {"name": name, "value": value} for name, value in course_fields_tupla if value is not None
            ]
        }
        
        if len(course_SemanticIdentifiers_tupla) == 0:
            return None, None
        
        return new_entity_course, course_ref
    
    
        """
        # Lista de tuplas complexas: (nome, valor, language_condicional, attributes_condicional)
lista_de_campos_complexos = [
    # Campo Fixo
    ("identifier.brcris", brcris_id_value, None, None),
    
    # Campo 'name' com language e attributes presentes
    (program_name, name_language, name_attributes),
    
    # Campo 'program_id' sem language, mas com attributes
    ("program_id", program_id, id_language, id_attributes), 
    
    # Campo 'description' que é None (deve ser excluído)
    ("description", program_description, None, None), 
]


# Compreensão de Lista: Chama a função e filtra todos os retornos None
fields = [
    # O resultado da função, que é um dicionário
    field_dict
    
    # Chama a função para cada conjunto de argumentos
    for name, value, lang, attrs in lista_de_campos_complexos
    if (field_dict := build_field_dict(name, value, lang, attrs)) is not None # Atribuição e Filtro (Walrus Operator)
]

        """