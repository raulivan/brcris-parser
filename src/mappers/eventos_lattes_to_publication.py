import json
from logging import Logger
import os
from typing import List
from util.text_validator import validar_titulo, validar_url_regex
from util.publication_type_mapping import BrCrisTypes, PublicationTypeMapping
from util.helper_nbr_rene import nbr_title
from validators.language_validator import LanguageValidator
from validators.journal_validator import JournalValidator
from validators.base_validator import BaseValidator
from util.unique_identifier_generator import brcrisid_generator
from util.text_transformers import capitalizar_nome, get_code_for_url, monta_areas_do_conhecimento, translate_type_of_publication, trata_string, extract_doi_from_url
from .base_mapper import BaseMapper


PUBLICATION_TYPE_ARTIGO = BrCrisTypes.CONFERENCIA

class EventosPlataformaLattes2PublicationMapper(BaseMapper):
    def get_source(self) -> str:
        return "PlataformaLattes"

    def transform(self, records: list[dict], logger:Logger, validators: List[BaseValidator] = []) -> list[dict]:
        """
        Converte registros de entrada para uma estrutura de dicionário
        pronta para ser convertida em XML pelo XMLWriter.
        """
        if records is None:
            return None

            
        language_validator = self.retrieve_validator_by_type(validators,LanguageValidator)
        
        # Relacionamento com cursos
        transformed_records = []

        for record_string in records:
            
            if record_string == None or len(record_string.strip()) == 0:
                continue


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
            # with open('meu_arquivo.json', 'w') as f:
            #     json.dump(record, f)
            #     continue

            record_node_authorships = self.get_field_value(record, "autores")
            areas_do_conhecimento  = self.get_field_value(record, "areas_do_conhecimento")
            palavras_chave  = self.get_field_value(record, "palavras_chave")

            # <field name="identifier.brcris" description="hash gerado com título + ano de publicação + tipo"/>
            part1 = self.get_field_value(record, "dados_basicos__titulo_do_trabalho")
            if validar_titulo(part1) == False:
                continue
            part2 = self.get_field_value(record, "dados_basicos__ano_do_trabalho")
            if part2 is None:
                continue

            part3 = PUBLICATION_TYPE_ARTIGO


            brcris_id_v1 = brcrisid_generator(part1,str(part2),part3)
            brcris_id_v2 = brcrisid_generator(part1,str(part2),part3,useReplaceHtmlChars=True)

            publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}"))
            publication_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
            if brcris_id_v1 != brcris_id_v2:
                publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v2}v2"))
                publication_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v2}v2"))
    
            # <field name="identifier.doi" description="id doi"/>
            doi_fora = self.get_field_value(record, "dados_basicos__doi")
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
            publication_identifier_isb = self.get_field_value(record, "detalhamento__isbn")
            publication_fields_identifier_tupla.append(("identifier.isbn", trata_string(publication_identifier_isb)))

            # <field name="identifier.dark"/>
            # TODO

            # <field name="identifier.other"/>
            # TODO

            # <field name="type"/> <!-- validar na lista de autoridade de tipos e gravar no idima PT (anteriormente era no coar)-->
            publication_fields_tupla.append(("type", PUBLICATION_TYPE_ARTIGO))

            # <field name="language"/> <!-- validar na lista de autoridade de idiomas e gravar no idima PT -->
            publication_language = self.get_field_value(record, "dados_basicos__idioma")
            if language_validator is not None:
                language_is_valid = language_validator.contains(dataset=None, target_value=publication_language)
                if language_is_valid:
                    publication_fields_tupla.append(("language", publication_language))

            # <field name="title"/> <!-- testar api de padronizacao do Rene -->
            publication_title = self.get_field_value(record, "dados_basicos__titulo_do_trabalho")
            if publication_title is not None:
                publication_title = nbr_title(publication_title)
                publication_fields_tupla.append(("title", publication_title))
			
            # <field name="subtitle"/>
            # TODO

            # <field name="alternativeTitle"/>
            publication_alternative_title = self.get_field_value(record, "dados_basicos__titulo_do_trabalho_ingles")
            if publication_alternative_title is not None and publication_alternative_title.strip() != "":
                publication_alternative_title = nbr_title(publication_alternative_title)
                if publication_alternative_title != publication_title:
                    publication_fields_tupla.append(("alternativeTitle", publication_alternative_title))
            
            # <field name="defenceDay"/> <!-- somente ano -->
            # TODO

            # <field name="publicationDate"/> <!-- somente ano -->
            publication_publicationDate = self.get_field_value(record, "dados_basicos__ano_do_trabalho")
            publication_fields_tupla.append(("publicationDate", trata_string(publication_publicationDate)))

            # <field name="degreeDate"/>
            # TODO

            # <field name="number"/>
            # TODO

            # <field name="volume"/>
            publication_volume = self.get_field_value(record, "detalhamento__volume")
            publication_fields_tupla.append(("volume", trata_string(publication_volume)))

            # <field name="issue"/>
            # TODO

            # <field name="series"/>
            publication_series = self.get_field_value(record, "detalhamento__serie")
            publication_fields_tupla.append(("series", trata_string(publication_series)))

            # <field name="edition"/>
            # TODO

            # <field name="startPage"/>
            publication_startPage = self.get_field_value(record, "detalhamento__pagina_inicial")
            publication_fields_tupla.append(("startPage", trata_string(publication_startPage)))

            # <field name="endPage"/>
            publication_endPage = self.get_field_value(record, "detalhamento__pagina_final")
            publication_fields_tupla.append(("endPage", trata_string(publication_endPage)))

            # <field name="author"/>
            if record_node_authorships is not None:
                for autor in record_node_authorships:
                    autor_name = self.get_field_value(autor, "nome_completo_do_autor")
                    if autor_name is not None:
                        publication_fields_tupla.append(("author", autor_name))


            # <field name="advisor"/>
            # TODO

            # <field name="coadvisor"/>
            # TODO

            # <field name="referee"/>
            # TODO

            # <field name="researchArea.cnpq" description="CNPq vocabullary code"/> <!-- nao precisa validar na lista de autoridade, mas deve ser captalizado corretamente. Deve concatenar toda a árvore em uma estrutura de diretorios. Ex.: Grande Area / Area / Sub-area / Especialidade -->
			
            if areas_do_conhecimento is not None:
                for area in areas_do_conhecimento:
                    grande_area = self.get_field_value(area, "nome_grande_area_do_conhecimento")
                    area_do_conhecimento = self.get_field_value(area, "nome_da_area_do_conhecimento")
                    sub_area = self.get_field_value(area, "nome_da_sub_area_do_conhecimento")
                    especialidade = self.get_field_value(area, "nome_da_especialidade")
                    
                    publication_fields_tupla.append(("researchArea.cnpq", monta_areas_do_conhecimento(grande_area=grande_area, area_do_conhecimento=area_do_conhecimento, sub_area=sub_area, especialidade=especialidade)))


            # <field name="researchArea.capes" description="CAPES vocabullary code"/> <!-- nao precisa validar na lista de autoridade, mas deve ser captalizado corretamente. Deve concatenar toda a árvore em uma estrutura de diretorios. Ex.: Grande Area / Area / Sub-area / Especialidade -->
			# TODO
            
            # <field name="researchArea.other" description="Other vocabullary code"/> <!-- nao precisa validar na lista de autoridade, mas deve ser captalizado corretamente. Deve concatenar toda a árvore em uma estrutura de diretorios. Ex.: Grande Area / Area / Sub-area / Especialidade -->
			# TODO

            # <field name="resourceUrl"/> <!-- Checar se é uma url -->
            publication_resourceUrl_1 = self.get_field_value(record, "dados_basicos__home_page_do_trabalho")
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
            publication_eventName = self.get_field_value(record, "detalhamento__nome_do_evento")
            publication_fields_tupla.append(("eventName", trata_string(publication_eventName)))

            publication_eventName2 = self.get_field_value(record, "detalhamento__nome_do_evento_ingles")
            publication_fields_tupla.append(("eventName", trata_string(publication_eventName2)))

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
            gerou_para_dono_Curriculo = False
            if record_node_authorships is not None:
                for autor in record_node_authorships:
                    new_author, author_ref, id_lattes_autor, order_autoria = self.__transform_person(autor)
                    if new_author is None:
                        continue
                    if id_curriculo_atual == id_lattes_autor:
                        gerou_para_dono_Curriculo = True
        
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

            if gerou_para_dono_Curriculo == False:
                # publication_fields_tupla.append(("author", self.get_field_value(record, "nome_completo")))
                new_author, author_ref, id_lattes_autor, order_autoria = self.__transform_person(record)
                if new_author is not None:
                    new_relation = {
                        "type": "Authorship",
                        "fromEntityRef": publication_ref, # fromEntity="Publication"
                        "toEntityRef":  author_ref, # toEntity="Person"
                        "attributes":[
                            # {"name": "order", "value": order_autoria} if order_autoria is not None else None,
                            # {"name": "affiliation", "value": affiliation} if affiliation is not None else None,
                            # {"name": "cnpqCodOrgUnit", "value": affiliation} if affiliation is not None else None
                        ]
                    } 
                    new_record["relations"].append(new_relation)
                    new_record["entities"].append(new_author)

            # Relacionamento com o Evento, deve ser feito aqui se for ter


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
        author_fields_identifier_tupla.append(("identifier.lattes", lattes_id_retorno))

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


    def __transform_event(self, journal_dict: dict, validator: JournalValidator = None) -> tuple[dict, str]:
        """
        Converte registros  de Revistas  
        """
        if validator is None:
            return None, None
        
        issn = self.get_field_value(journal_dict, "detalhamento__issn")

        if not self.has_value(issn):
            return None, None
        

        journal_is_valid, key_journal= validator.is_valid(f"issn::{issn}")
        if not journal_is_valid:
            return None, None
        
        journal_SemanticIdentifiers_tupla = []
        journal_fields_identifier_tupla = []
        journal_fields_tupla = []
        
                
        journal_SemanticIdentifiers_tupla.append(("issn", f"issn::{issn}"))
        journal_fields_identifier_tupla.append(("identifier.issn", issn))
            
        # Gerando a referência deste registro para relacionamentos
        journal_ref = self.creat_ref_identifier()

    
        new_entity_journal= {
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
        
        if len(journal_SemanticIdentifiers_tupla) == 0:
            return None, None
        
        
        return new_entity_journal, journal_ref
      
    