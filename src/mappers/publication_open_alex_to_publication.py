import json
import os
from typing import List
from util.publication_type_mapping import PublicationTypeMapping
from util.helper_nbr_rene import nbr_title
from validators.language_validator import LanguageValidator
from validators.journal_validator import JournalValidator
from validators.base_validator import BaseValidator
from util.unique_identifier_generator import brcrisid_generator
from util.text_transformers import capitalizar_nome, get_code_for_url, trata_string, extract_doi_from_url
from .base_mapper import BaseMapper



class PublicationOpenAlex2PublicationMapper(BaseMapper):
    def get_source(self) -> str:
        return "OpenAlex"

    def transform(self, records: list[dict], validators: List[BaseValidator] = []) -> list[dict]:
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

            # Recuperando a tag de Ids da OpenAlex
            record_node_ids = self.get_field_value(record, "ids")
            record_node_biblio = self.get_field_value(record, "biblio")
            record_node_authorships = self.get_field_value(record, "authorships")
            record_node_primary_location = self.get_field_value(record, "primary_location")
            record_node_keywords = self.get_field_value(record, "keywords")
            record_node_locations = self.get_field_value(record, "locations")        
            
             
            #<field name="identifier.brcris" description="hash gerado com título + ano de publicação + tipo"/>
            part1 = self.get_field_value(record, "title")
            part2 = self.get_field_value(record, "publication_year")
            temp_tipo = self.get_field_value(record, "type")
            part3 = PublicationTypeMapping.get_brcris_type(temp_tipo, "OPENALEX")

            if part3 is None:
                # Não tem um tipo válido de publicação... pula pro próximo
                continue


            brcris_id_v1 = brcrisid_generator(part1,str(part2),part3)
            brcris_id_v2 = brcrisid_generator(part1,str(part2),part3,useReplaceHtmlChars=True)

            publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}"))
            publication_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
            if brcris_id_v1 != brcris_id_v2:
                publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v2}v2"))
                publication_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v2}v2"))
    
            # <field name="identifier.doi" description="id doi"/>
            doi_fora = self.get_field_value(record, "doi")
            if self.has_value(doi_fora):
                doi_fora = extract_doi_from_url(doi_fora)
            
            if  self.has_value(doi_fora):
                publication_SemanticIdentifiers_tupla.append(("doi", f"doi::{doi_fora}"))
                publication_fields_identifier_tupla.append(("identifier.doi", doi_fora))

            doi_ids = self.get_field_value(record_node_ids, "doi")
            if self.has_value(doi_ids):
                doi_ids = extract_doi_from_url(doi_ids)

            if doi_fora != doi_ids:
                if self.has_value(doi_ids):
                    publication_SemanticIdentifiers_tupla.append(("doi", f"doi::{doi_ids}"))
                    publication_fields_identifier_tupla.append(("identifier.doi", doi_ids))


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
            id_open_alex = self.get_field_value(record, "id")
            if not id_open_alex is None:
                id_open_alex = get_code_for_url(id_open_alex)
            publication_fields_identifier_tupla.append(("identifier.other", id_open_alex))
            id_open_alex_ids = self.get_field_value(record_node_ids, "id")
            if not id_open_alex_ids is None:
                id_open_alex_ids = get_code_for_url(id_open_alex_ids)
            if id_open_alex != id_open_alex_ids:
                publication_fields_identifier_tupla.append(("identifier.other", id_open_alex_ids))

            # <field name="type"/> <!-- validar na lista de autoridade de tipos e gravar no idima PT (anteriormente era no coar)-->
            publication_type = PublicationTypeMapping.get_brcris_type(self.get_field_value(record, "type"), "OPENALEX")
            if publication_type is None:
                continue

            publication_fields_tupla.append(("type", publication_type))

            # <field name="language"/> <!-- validar na lista de autoridade de idiomas e gravar no idima PT -->
            publication_language = self.get_field_value(record, "language")
            if language_validator is not None:
                language_is_valid, key_language = language_validator.is_valid(publication_language)
                if language_is_valid:
                    publication_language = key_language

            publication_fields_tupla.append(("language", publication_language))

            # <field name="title"/> <!-- testar api de padronizacao do Rene -->
            publication_title = self.get_field_value(record, "title")
            if publication_title is not None:
                # publication_title = capitalizar_nome(publication_title)
                publication_title = nbr_title(publication_title)
                
                publication_fields_tupla.append(("title", publication_title))
			
            # <field name="subtitle"/>
            # TODO

            # <field name="alternativeTitle"/>
            publication_alternative_title = self.get_field_value(record, "display_name")
            if publication_alternative_title is not None:
                # publication_alternative_title = capitalizar_nome(publication_alternative_title)
                publication_alternative_title = nbr_title(publication_alternative_title)
                if publication_alternative_title != publication_title:
                    publication_fields_tupla.append(("alternativeTitle", publication_alternative_title))
            
            # <field name="defenceDay"/> <!-- somente ano -->
            # TODO

            # <field name="publicationDate"/> <!-- somente ano -->
            publication_publicationDate = self.get_field_value(record, "publication_year")
            publication_fields_tupla.append(("publicationDate", trata_string(publication_publicationDate)))

            # <field name="degreeDate"/>
            # TODO

            # <field name="number"/>
            # TODO

            # <field name="issue"/>
            publication_issue = self.get_field_value(record_node_biblio, "issue")
            publication_fields_tupla.append(("issue",  trata_string(publication_issue)))
            
            
            # <field name="volume"/>
            publication_volume= self.get_field_value(record_node_biblio, "volume")
            publication_fields_tupla.append(("volume",  trata_string(publication_volume)))

            # <field name="series"/>
            # TODO

            # <field name="edition"/>
            # TODO

            # <field name="startPage"/>
            publication_startPage = self.get_field_value(record_node_biblio, "first_page")
            publication_fields_tupla.append(("startPage",  trata_string(publication_startPage)))

            # <field name="endPage"/>
            publication_endPage = self.get_field_value(record_node_biblio, "last_page")
            publication_fields_tupla.append(("endPage",  trata_string(publication_endPage)))

            # <field name="author"/>
            for autor in record_node_authorships:
                autor_node = self.get_field_value(autor, "author")
                autor_name = self.get_field_value(autor_node, "display_name")
                publication_fields_tupla.append(("author", autor_name))

            # <field name="advisor"/>
            # TODO

            # <field name="coadvisor"/>
            # TODO

            # <field name="referee"/>
            # TODO

            # <field name="researchArea.cnpq" description="CNPq vocabullary code"/> <!-- nao precisa validar na lista de autoridade, mas deve ser captalizado corretamente. Deve concatenar toda a árvore em uma estrutura de diretorios. Ex.: Grande Area / Area / Sub-area / Especialidade -->
			# TODO
            
            # <field name="researchArea.capes" description="CAPES vocabullary code"/> <!-- nao precisa validar na lista de autoridade, mas deve ser captalizado corretamente. Deve concatenar toda a árvore em uma estrutura de diretorios. Ex.: Grande Area / Area / Sub-area / Especialidade -->
			# TODO
            
            # <field name="researchArea.other" description="Other vocabullary code"/> <!-- nao precisa validar na lista de autoridade, mas deve ser captalizado corretamente. Deve concatenar toda a árvore em uma estrutura de diretorios. Ex.: Grande Area / Area / Sub-area / Especialidade -->
			# TODO

            # <field name="resourceUrl"/> <!-- Checar se é uma url -->
            publication_resourceUrl_1 = self.get_field_value(record_node_primary_location, "landing_page_url")
            publication_fields_tupla.append(("resourceUrl",  trata_string(publication_resourceUrl_1)))

            publication_resourceUrl_2 = self.get_field_value(record_node_primary_location, "pdf_url")
            publication_fields_tupla.append(("resourceUrl",  trata_string(publication_resourceUrl_2)))
			

            # <field name="rights"/>
            # TODO

            # <field name="license"/>
            publication_license = self.get_field_value(record_node_primary_location, "license")
            publication_fields_tupla.append(("license",  trata_string(publication_license)))

            # <field name="keyword"/> <!-- testar api de padronizacao do Rene -->
            for keyw in record_node_keywords:
                keyword = self.get_field_value(keyw, "display_name")
                if keyword is not None:
                    keyword = capitalizar_nome(keyword)

                    publication_fields_tupla.append(("keyword", keyword))
            
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

            # Relacionamento com os autores
            for item in record_node_authorships:
                # Somente com autores que tem ORCID
                autor_node = self.get_field_value(item, "author")
                orcid = self.get_field_value(autor_node, "orcid")
                if orcid is not None:
                    new_author, author_ref  = self.__transform_person(item["author"])
                    if new_author is None:
                        continue

                    order = self.get_field_value(item, "author_position")

                    affiliation = None
                    institutions = self.get_field_value(item, "institutions")

                    if not institutions is None:
                        if len(institutions) > 0:
                            affiliation = self.get_field_value(institutions[0], "display_name")
                            if not affiliation is None:
                                affiliation = capitalizar_nome(affiliation)   

                    new_relation = {
                        "type": "Authorship",
                        "fromEntityRef": publication_ref, # fromEntity="Publication"
                        "toEntityRef":  author_ref, # toEntity="Person"
                        "attributes":[
                            {"name": "order", "value": order} if order is not None else None,
                            {"name": "affiliation", "value": affiliation} if affiliation is not None else None
                        ]
                    } 
                    
                    new_record["relations"].append(new_relation)
                    new_record["entities"].append(new_author)
            
            # Relacionamento com a revista
            journal_validator = self.retrieve_validator_by_type(validators,JournalValidator)
            for item in record_node_locations:     

                new_journal, journal_ref = self.__transform_journal(item, journal_validator)
                if new_journal is None:
                    continue
                    
                new_relation = {
                    "type": "PublisherJournal",
                    "fromEntityRef": publication_ref, # fromEntity="Publication" 
                    "toEntityRef":  journal_ref # toEntity="Journal"
                } 
                
                new_record["relations"].append(new_relation)
                new_record["entities"].append(new_journal)
            
            transformed_records.append(new_record)
        return transformed_records

    def __transform_person(self, author_dict: dict) -> tuple[dict, str]:
        """
        Converte registros  de autores  
        """
       
        author_SemanticIdentifiers_tupla = []
        author_fields_identifier_tupla = []
        author_fields_tupla = []

        openalex_id = self.get_field_value(author_dict, "id")
        if not openalex_id is None:
            openalex_id = get_code_for_url(openalex_id)
        
        orcid_id = self.get_field_value(author_dict, "orcid")
        if not orcid_id is None:
            orcid_id = get_code_for_url(orcid_id)

        # author_SemanticIdentifiers_tupla.append(("openalex", f"openalex::{openalex_id}"))
        author_fields_identifier_tupla.append(("identifier.openalex", openalex_id))

        author_SemanticIdentifiers_tupla.append(("orcid", f"orcid::{orcid_id}"))
        author_fields_identifier_tupla.append(("identifier.orcid", orcid_id))

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
            return None, None
        
        
        return new_entity_person, author_ref
      
    def __transform_journal(self, journal_dict: dict, validator: JournalValidator = None) -> tuple[dict, str]:
        """
        Converte registros  de Revistas  
        """
        if validator is None:
            return None, None
        
        source_node = self.get_field_value(journal_dict, "source")
        lista_issn = self.get_field_value(source_node, "issn")
        if lista_issn is None:
            return None, None
        
        if not isinstance(lista_issn, list):
            lista_issn = [lista_issn]
        
        if len(lista_issn) == 0:
            return None, None
        

        journal_SemanticIdentifiers_tupla = []
        journal_fields_identifier_tupla = []
        journal_fields_tupla = []
        
        for item_issn in lista_issn:
            if not self.has_value(item_issn):
                continue

            journal_is_valid, key_orgunit = validator.is_valid(f"issn::{item_issn}")
            if not journal_is_valid:
                return None, None
            
                   
            journal_SemanticIdentifiers_tupla.append(("issn", f"issn::{item_issn}"))
            journal_fields_identifier_tupla.append(("identifier.issn", item_issn))
        		
        
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