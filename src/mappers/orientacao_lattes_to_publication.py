import json
import os
from typing import List
from util.helper_nbr_rene import nbr_title
from validators.language_validator import LanguageValidator
from validators.journal_validator import JournalValidator
from validators.base_validator import BaseValidator
from util.unique_identifier_generator import brcrisid_generator
from util.text_transformers import capitalizar_nome, get_code_for_url, translate_type_of_publication, trata_string, extract_doi_from_url
from .base_mapper import BaseMapper



class OrientacaoPlataformaLattes2PublicationMapper(BaseMapper):
    def get_source(self) -> str:
        return "PlataformaLattes"

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

            record_node_authorships = self.get_field_value(record, "orientado")
 
           
             
            #<field name="identifier.brcris" description="hash gerado com título + ano de publicação + tipo"/>
            part1 = self.get_field_value(record, "dados_basicos_de_outras_orientacoes_concluidas__titulo")
            part2 = self.get_field_value(record, "dados_basicos_de_outras_orientacoes_concluidas__ano")
            part3 = translate_type_of_publication(self.get_field_value(record, "dados_basicos_de_outras_orientacoes_concluidas__natureza"))

            brcris_id_v1 = brcrisid_generator(part1,str(part2),part3)
            brcris_id_v2 = brcrisid_generator(part1,str(part2),part3,useReplaceHtmlChars=True)

            publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}"))
            publication_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
            if brcris_id_v1 != brcris_id_v2:
                publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v2}v2"))
                publication_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v2}v2"))
    
            # <field name="identifier.doi" description="id doi"/>
            doi_fora = self.get_field_value(record, "dados_basicos_de_outras_orientacoes_concluidas__doi")
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
            publication_type = translate_type_of_publication(self.get_field_value(record, "dados_basicos_de_outras_orientacoes_concluidas__natureza"))
            publication_fields_tupla.append(("type", publication_type))

            # <field name="language"/> <!-- validar na lista de autoridade de idiomas e gravar no idima PT -->
            publication_language = self.get_field_value(record, "dados_basicos_de_outras_orientacoes_concluidas__idioma")
            if language_validator is not None:
                language_is_valid = language_validator.contains(dataset=None, target_value=publication_language)
                if language_is_valid:
                    publication_fields_tupla.append(("language", publication_language))

            # <field name="title"/> <!-- testar api de padronizacao do Rene -->
            publication_title = self.get_field_value(record, "dados_basicos_de_outras_orientacoes_concluidas__titulo")
            if publication_title is not None:
                publication_title = nbr_title(publication_title)
                publication_fields_tupla.append(("title", publication_title))
			
            # <field name="subtitle"/>
            # TODO

            # <field name="alternativeTitle"/>
            publication_alternative_title = self.get_field_value(record, "dados_basicos_de_outras_orientacoes_concluidas__titulo_ingles")
            if publication_alternative_title is not None:
                publication_alternative_title = nbr_title(publication_alternative_title)
                if publication_alternative_title != publication_title:
                    publication_fields_tupla.append(("alternativeTitle", publication_alternative_title))
            
            # <field name="defenceDay"/> <!-- somente ano -->
            publication_defenceDay = self.get_field_value(record, "dados_basicos_de_outras_orientacoes_concluidas__ano")
            publication_fields_tupla.append(("defenceDay", trata_string(publication_defenceDay)))

            # <field name="publicationDate"/> <!-- somente ano -->
            publication_publicationDate = self.get_field_value(record, "dados_basicos_de_outras_orientacoes_concluidas__ano")
            publication_fields_tupla.append(("publicationDate", trata_string(publication_publicationDate)))

            # <field name="degreeDate"/>
            # TODO

            # <field name="number"/>
            # TODO

            # <field name="issue"/>
            # TODO
            
            # <field name="volume"/>
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
          
            autor_name = self.get_field_value(record_node_authorships, "nome")
            publication_fields_tupla.append(("author", autor_name))

            # <field name="advisor"/>
            orientador_name = self.get_field_value(record, "nome_completo")
            publication_fields_tupla.append(("advisor", orientador_name))

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
            publication_resourceUrl_1 = self.get_field_value(record, "dados_basicos_de_outras_orientacoes_concluidas__home_page")
            publication_fields_tupla.append(("resourceUrl",  trata_string(publication_resourceUrl_1)))			

            # <field name="rights"/>
            # TODO

            # <field name="license"/>
            # TODO

            # <field name="keyword"/> <!-- testar api de padronizacao do Rene -->
            # TODO
            
            # <field name="abstract"/>
			# TODO

            # <field name="status"/>
            publication_situacao = self.get_field_value(record, "situacao")
            publication_fields_tupla.append(("resourceUrl",  trata_string(publication_situacao)))		

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

            # Relacionamento com o orientador
            new_author, author_ref  = self.__transform_person(record)
            if new_author is None:
                continue

            new_relation = {
                "type": "Adivisoring",
                "fromEntityRef": publication_ref, # fromEntity="Publication"
                "toEntityRef":  author_ref, # toEntity="Person"
                # "attributes":[
                    # {"name": "order", "value": order} if order is not None else None,
                    # {"name": "affiliation", "value": affiliation} if affiliation is not None else None,
                    # {"name": "cnpqCodOrgUnit", "value": affiliation} if affiliation is not None else None
                # ]
            } 
            
            new_record["relations"].append(new_relation)
            new_record["entities"].append(new_author)
            
            transformed_records.append(new_record)
        return transformed_records

    def __transform_person(self, author_dict: dict) -> tuple[dict, str]:
        """
        Converte registros  de autores  
        """
       
        author_SemanticIdentifiers_tupla = []
        author_fields_identifier_tupla = []
        author_fields_tupla = []

        
        lattes_id = self.get_field_value(author_dict, "id")
        if lattes_id is None:
            return None, None

        author_SemanticIdentifiers_tupla.append(("lattes", f"lattes::{lattes_id}"))
        author_fields_identifier_tupla.append(("identifier.lattes", lattes_id))

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
      
    