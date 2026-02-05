import json
from logging import Logger
import os
from typing import List
from validators.person_validator import PersonValidator
from validators.course_validator import CourseValidator
from validators.orgunit_validator import OrgUnitValidator
from util.text_validator import validar_titulo, validar_url_regex
from util.publication_type_mapping import BrCrisTypes
from util.helper_nbr_rene import nbr_title
from validators.language_validator import LanguageValidator
from validators.base_validator import BaseValidator
from util.unique_identifier_generator import brcrisid_generator
from util.text_transformers import trata_string, extract_doi_from_url
from .base_mapper import BaseMapper


PUBLICATION_TYPE = BrCrisTypes.DISSERTACAO

class OrientacaoPlataformaLattes2MestradoPublicationMapper(BaseMapper):
    def get_source(self) -> str:
        return "PlataformaLattes"

    def transform(self, records: list[dict], logger:Logger, validators: List[BaseValidator] = []) -> list[dict]:
        """
        Converte registros de entrada para uma estrutura de dicionário
        pronta para ser convertida em XML pelo XMLWriter.
        """
        if records is None:
            return None

        person_validator = self.retrieve_validator_by_type(validators,PersonValidator)
        if person_validator is None:
            raise "PersonValidator not found in validators list"
            
        language_validator = self.retrieve_validator_by_type(validators,LanguageValidator)
        
        # Relacionamento com cursos
        transformed_records = []

        for record_string in records:
            
            if record_string == None or len(record_string.strip()) == 0:
                continue

            ORIDENTADOR = True
            # Identificador semanticos 
            publication_SemanticIdentifiers_tupla = []
            # Campos Identificador
            publication_fields_identifier_tupla = []
            # Campos field
            publication_fields_tupla = []
            
            # Gerando a referência deste registro para relacionamentos
            publication_ref = self.creat_ref_identifier()
            print(f"Processando registro: {publication_ref}")
            
            record =  json.loads(record_string)

            part3 = self.get_field_value(record, "nivel")
            if part3 is None:
                continue
            if part3 == "ORIENTACOES-CONCLUIDAS-PARA-MESTRADO":
                part3 = PUBLICATION_TYPE
            else:
                continue         


            record_node_authorships = self.get_field_value(record, "orientado")
            palavras_chave  = self.get_field_value(record, "palavras_chave")

            # <field name="identifier.brcris" description="hash gerado com título + ano de publicação + tipo"/>
            part1 = self.get_field_value(record, "dados_basicos_de_orientacoes_concluidas_para_mestrado__titulo")
            if validar_titulo(part1) == False:
                continue
            part2 = self.get_field_value(record, "dados_basicos_de_orientacoes_concluidas_para_mestrado__ano")
            if part2 is None:
                continue

            

            brcris_id_v1 = brcrisid_generator(part1,str(part2),part3)
            brcris_id_v2 = brcrisid_generator(part1,str(part2),part3,useReplaceHtmlChars=True)

            publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}"))
            publication_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
            if brcris_id_v1 != brcris_id_v2:
                publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v2}v2"))
                publication_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v2}v2"))
    
            # <field name="identifier.doi" description="id doi"/>
            doi_fora = self.get_field_value(record, "dados_basicos_de_orientacoes_concluidas_para_mestrado__doi")
            if self.has_value(doi_fora):
                doi_fora = extract_doi_from_url(doi_fora)
            
            if  self.has_value(doi_fora):
                publication_SemanticIdentifiers_tupla.append(("doi", f"doi::{doi_fora}"))
                publication_fields_identifier_tupla.append(("identifier.doi", doi_fora))


            #<field name="identifier.capes" description="id capes"/>
            # TODO

            # <field name="identifier.bdtd"/>
            # TODO

            # <field name="identifier.oasisbr"/>
            # TODO

            # <field name="identifier.handle"/>
            # TODO

            # <field name="identifier.pmcid"/>
            # TODO

            # <field name="identifier.isi-number"/>
            # TODO

            # <field name="identifier.scp-number"/>
            # TODO

            # <field name="identifier.issn"/>
            # TODO

            # <field name="identifier.issn"/>
            # TODO

            # <field name="identifier.isbn"/>
            # TODO

            # <field name="identifier.dark"/>
            # TODO

            # <field name="identifier.other"/>
            # TODO

            # <field name="type"/> <!-- validar na lista de autoridade de tipos e gravar no idima PT (anteriormente era no coar)-->
            publication_fields_tupla.append(("type", PUBLICATION_TYPE))

            # <field name="language"/> <!-- validar na lista de autoridade de idiomas e gravar no idima PT -->
            publication_language = self.get_field_value(record, "dados_basicos_de_orientacoes_concluidas_para_mestrado__idioma")
            if language_validator is not None:
                language_is_valid = language_validator.contains(dataset=None, target_value=publication_language)
                if language_is_valid:
                    publication_fields_tupla.append(("language", publication_language))

            # <field name="title"/> <!-- testar api de padronizacao do Rene -->
            publication_title = self.get_field_value(record, "dados_basicos_de_orientacoes_concluidas_para_mestrado__titulo")
            if publication_title is not None:
                publication_title = nbr_title(publication_title)
                publication_fields_tupla.append(("title", publication_title))
			
            # <field name="subtitle"/>
            # TODO

            # <field name="alternativeTitle"/>
            publication_alternative_title = self.get_field_value(record, "dados_basicos_de_orientacoes_concluidas_para_mestrado__titulo_ingles")
            if publication_alternative_title is not None and publication_alternative_title.strip() != "":
                publication_alternative_title = nbr_title(publication_alternative_title)
                if publication_alternative_title != publication_title:
                    publication_fields_tupla.append(("alternativeTitle", publication_alternative_title))
            
            # <field name="defenceDay"/> <!-- somente ano -->
            # TODO

            # <field name="publicationDate"/> <!-- somente ano -->
            publication_publicationDate = self.get_field_value(record, "dados_basicos_de_orientacoes_concluidas_para_mestrado__ano")
            publication_fields_tupla.append(("publicationDate", trata_string(publication_publicationDate)))

            # <field name="degreeDate"/>
            publication_degreeDatee = self.get_field_value(record, "dados_basicos_de_orientacoes_concluidas_para_mestrado__ano")
            publication_fields_tupla.append(("degreeDate", trata_string(publication_degreeDatee)))

            # <field name="number"/>
            # TODO

            # <field name="volume"/>
            # TODO

            # <field name="issue"/>
            # TODO

            # <field name="series"/>
            # TODO

            # <field name="edition"/>
            # TODO

            # <field name="startPage"/>
            # TODO

            # <field name="endPage"/>
            # TODO

            # <field name="author"/>
            if record_node_authorships is not None:
                autor_name = self.get_field_value(record_node_authorships, "nome")
                if autor_name is not None:
                    publication_fields_tupla.append(("author", autor_name))


            # <field name="advisor"/>
            tipo = self.get_field_value(record, "detalhamento_de_orientacoes_concluidas_para_mestrado__tipo_de_orientacao")
            if (tipo == None or tipo.strip() == "" or tipo == 'ORIENTADOR_PRINCIPAL'):
                ORIDENTADOR = True
                publication_advisor = self.get_field_value(record, "nome_completo")
                publication_fields_tupla.append(("advisor", trata_string(publication_advisor)))
            else:
            # <field name="coadvisor"/>
                ORIDENTADOR = False
                publication_coadvisor = self.get_field_value(record, "nome_completo")
                publication_fields_tupla.append(("coadvisor", trata_string(publication_coadvisor)))

            # <field name="referee"/>
            # TODO

            # <field name="researchArea.cnpq" description="CNPq vocabullary code"/> <!-- nao precisa validar na lista de autoridade, mas deve ser captalizado corretamente. Deve concatenar toda a árvore em uma estrutura de diretorios. Ex.: Grande Area / Area / Sub-area / Especialidade -->
			# TODO
            
            # <field name="researchArea.capes" description="CAPES vocabullary code"/> <!-- nao precisa validar na lista de autoridade, mas deve ser captalizado corretamente. Deve concatenar toda a árvore em uma estrutura de diretorios. Ex.: Grande Area / Area / Sub-area / Especialidade -->
			# TODO
            
            # <field name="researchArea.other" description="Other vocabullary code"/> <!-- nao precisa validar na lista de autoridade, mas deve ser captalizado corretamente. Deve concatenar toda a árvore em uma estrutura de diretorios. Ex.: Grande Area / Area / Sub-area / Especialidade -->
			# TODO

            # <field name="resourceUrl"/> <!-- Checar se é uma url -->
            publication_resourceUrl_1 = self.get_field_value(record, "dados_basicos_de_orientacoes_concluidas_para_mestrado__home_page")
            if publication_resourceUrl_1 is not None:
                publication_resourceUrl_1 = publication_resourceUrl_1.replace("[","")
                publication_resourceUrl_1 = publication_resourceUrl_1.replace("]","")
                if validar_url_regex(publication_resourceUrl_1) == True:
                    publication_fields_tupla.append(("resourceUrl",  trata_string(publication_resourceUrl_1)))			

            # <field name="rights"/>
            # TODO

            # <field name="license"/>
            # TODO

            # <field name="keyword"/> <!-- testar api de padronizacao do Rene -->
            if palavras_chave is not None:
                for palavra_chave in palavras_chave:
                    if palavra_chave is None:
                        continue
                    if len(palavra_chave.strip()) == 0:
                        continue

                    publication_fields_tupla.append(("keyword", palavra_chave))

            
            # <field name="abstract"/>
			# TODO

            # <field name="status"/>
            # TODO		

            # <field name="coverage"/>
            # TODO

            # <field name="references"/>
             # TODO
			
            #<field name="accessType" description="COAR Rights Types"/> <!-- validar na lista de autoridade de tipos de acesso (baseado no coar) e gravar no idima PT -->
			# TODO

			# <field name="eventName"/> <!-- caso seja uma publicacao em anais de eventos -->
            # TODO

            # Monta a estrutura que o XMLWriter espera
            new_entity_publication = {
                "entity_attribs": {
                    "type": "Publication",
                    "ref": publication_ref
                },
                "semantic_identifiers":[
                    {"name": name, "value": value} for name, value in publication_SemanticIdentifiers_tupla if value is not None
                ],
                "fields_identifier": [
                    {"name": name, "value": value} for name, value in publication_fields_identifier_tupla if value is not None
                ],
                "fields": [
                    {"name": name, "value": value} for name, value in publication_fields_tupla if value is not None
                ]
            }

            new_record = {
                "entities": [new_entity_publication],
                "relations":[]
            }

            # Relacionamento com o dono do curriculo
            id_curriculo_atual = self.get_field_value(record, "id")
            new_adivisoring, adivisoring_ref, id_lattes_autor, order_autoria = self.__transform_person(record)
            if new_adivisoring is not None:
                if ORIDENTADOR == True:

                    new_relation = {
                        "type": "Adivisoring",
                        "fromEntityRef": publication_ref, # fromEntity="Publication"
                        "toEntityRef":  adivisoring_ref, # toEntity="Person"
                        "attributes":[
                            # {"name": "order", "value": order_autoria} if order_autoria is not None else None,
                            # {"name": "affiliation", "value": affiliation} if affiliation is not None else None,
                            # {"name": "cnpqCodOrgUnit", "value": affiliation} if affiliation is not None else None
                        ]
                    } 
                    new_record["relations"].append(new_relation)
                else:
                    new_relation = {
                        "type": "CoAdivisoring",
                        "fromEntityRef": publication_ref, # fromEntity="Publication"
                        "toEntityRef":  adivisoring_ref, # toEntity="Person"
                        "attributes":[
                            # {"name": "order", "value": order_autoria} if order_autoria is not None else None,
                            # {"name": "affiliation", "value": affiliation} if affiliation is not None else None,
                            # {"name": "cnpqCodOrgUnit", "value": affiliation} if affiliation is not None else None
                        ]
                    } 
                    new_record["relations"].append(new_relation)

                new_record["entities"].append(new_adivisoring)

            # Relacionamento com os autores/orientado
            if record_node_authorships is not None:
                
                new_author, author_ref, id_lattes_autor, order_autoria = self.__transform_person(record_node_authorships)
                if not new_author is None:
                    if person_validator.is_valid(id_lattes_autor):
                        new_relation = {
                            "type": "Authorship",
                            "fromEntityRef": publication_ref, # fromEntity="Publication"
                            "toEntityRef":  author_ref, # toEntity="Person"
                            "attributes":[
                                {"name": "order", "value": order_autoria} if order_autoria is not None else None,
                                # {"name": "affiliation", "value": affiliation} if affiliation is not None else None,
                                # {"name": "cnpqCodOrgUnit", "value": affiliation} if affiliation is not None else None
                            ]
                        } 
                        new_record["relations"].append(new_relation)
                        new_record["entities"].append(new_author)

            # Relacionamento com a instituição
            orgunit_validator = self.retrieve_validator_by_type(validators,OrgUnitValidator)

            new_orgunit, orgunit_ref= self.__transform_orgunit(record, orgunit_validator)
            if new_orgunit is not None:
                new_relation = {
                    "type": "ThesisSponsorship",
                    "fromEntityRef": orgunit_ref, # fromEntity="OrgUnit"
                    "toEntityRef":  publication_ref # toEntity="Publication"
                } 
                
                new_record["relations"].append(new_relation)
                new_record["entities"].append(new_orgunit)
            
            # Relacionamento com o curso
            course_validator = self.retrieve_validator_by_type(validators,CourseValidator)

            new_course, course_ref= self.__transform_course(record, course_validator)
            if new_course is not None:
                new_relation = {
                    "type": "CourseThesis",
                    "fromEntityRef": course_ref, # fromEntity="Course"
                    "toEntityRef":  publication_ref # toEntity="Publication"
                } 
                
                new_record["relations"].append(new_relation)
                new_record["entities"].append(new_course)
            
            transformed_records.append(new_record)
        return transformed_records

    def __transform_person(self, author_dict: dict) -> tuple[dict, str]:
        """
        Converte registros  de autores  
        """
        lattes_id_retorno = None
        order = None
        author_SemanticIdentifiers_tupla = []
        author_fields_identifier_tupla = []
        author_fields_tupla = []

        
        lattes_id_curriculo = self.get_field_value(author_dict, "id")
        if lattes_id_curriculo is None:
            # Trata de mais autores
            lattes_id_autor = self.get_field_value(author_dict, "nro_id_cnpq")
            if lattes_id_autor is None or len(lattes_id_autor.strip()) == 0:
                return None, None, None, None
            lattes_id_retorno = lattes_id_autor
            order = self.get_field_value(author_dict, "ordem_de_autoria")
        else:
            lattes_id_retorno = lattes_id_curriculo


        author_SemanticIdentifiers_tupla.append(("lattes", f"lattes::{lattes_id_retorno}"))

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
        
        
        return new_entity_person, author_ref, lattes_id_retorno, order


    def __transform_orgunit(self, orgunit_dict: dict, validator: OrgUnitValidator = None) -> tuple[dict, str]:
        """
        Converte registros  de cursos  
        """
        if validator is None:
            return None, None
        
        orgunit_SemanticIdentifiers_tupla = []
        orgunit_fields_identifier_tupla = []
        orgunit_fields_tupla = []
        
        
        nome_instituicao = self.get_field_value(orgunit_dict, "detalhamento_de_orientacoes_concluidas_para_mestrado__nome_da_instituicao")
        
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
        
        if len(orgunit_SemanticIdentifiers_tupla) == 0:
            return None, None
        
        
        return new_entity_orgunit, orgunit_ref
      
    def __transform_course(self, course: dict, validator: CourseValidator = None) -> tuple[dict, str]:
        """
        Converte registros  de cursos  
        """
        course_SemanticIdentifiers_tupla = []
        course_fields_identifier_tupla = []
        course_fields_tupla = []
        
        # Gerando a referência deste registro para relacionamentos
        course_ref = self.creat_ref_identifier()

        # <field name="name"/>
        course_name = self.get_field_value(course, "detalhamento_de_orientacoes_concluidas_para_mestrado__nome_do_curso")
        if course_name == None:
            return None
        
        course_name = trata_string(course_name)
        if course_name== "":
            return None, None
        
        course_name_instituicao = self.get_field_value(course, "detalhamento_de_orientacoes_concluidas_para_mestrado__nome_da_instituicao")
        if course_name_instituicao == None:
            return None
        
        course_name_instituicao = trata_string(course_name_instituicao)
        if course_name_instituicao== "":
            return None, None
        
        # Gera BRCRISid para validação
        course_brcris_id_v1 = brcrisid_generator(course_name,course_name_instituicao, 'Mestrado')        
        
        key_validacao = f"brcris_{course_brcris_id_v1}"
        course_is_valid, key_course = validator.is_valid(description=key_validacao)
            
        if not course_is_valid:
            course_brcris_id_v1 = brcrisid_generator(course_name,course_name_instituicao, 'Mestrado/Doutorado')        
            key_validacao = f"brcris_{course_brcris_id_v1}"
            course_is_valid, key_course = validator.is_valid(description=key_validacao)
            if not course_is_valid:
                return None, None   
       
        course_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{course_brcris_id_v1}"))
                                
        
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