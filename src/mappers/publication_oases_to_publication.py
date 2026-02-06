import json
from logging import Logger
from typing import List

# Importando os validators
from validators.base_validator import BaseValidator
from validators.person_validator import PersonValidator
from validators.course_validator import CourseValidator
from validators.publication_artigo_validator import PublicationArtigoValidator
from validators.publication_capitulo_livro_validator import PublicationCapituloLivroValidator
from validators.publication_doi_validator import PublicationDOIValidator
from validators.publication_eventos_validator import PublicationEventosValidator
from validators.publication_formacao_validator import PublicationFormacaoValidator
from validators.publication_livros_validator import PublicationLivrosValidator
from validators.publication_orcid_validator import PublicationORCIDValidator
from validators.publication_orientacoes_validator import PublicationOrientacoesValidator

# IMportando LIBs auxiliares
from util.text_validator import validar_titulo
from util.publication_type_mapping import BrCrisTypes, PublicationTypeMapping
from util.helper_nbr_rene import nbr_title
from util.unique_identifier_generator import brcrisid_generator
from util.text_transformers import trata_string

# Importando omapeador base
from .base_mapper import BaseMapper


class PublicationOASIS2PublicationMapper(BaseMapper):
    def get_source(self) -> str:
        return "OASIS"

    def transform(self, records: list[dict], logger:Logger, validators: List[BaseValidator] = []) -> list[dict]:
        """
        Converte registros de entrada para uma estrutura de dicionário
        pronta para ser convertida em XML pelo XMLWriter.
        """
        if records is None:
            return None

        publicationArtigoValidator = self.retrieve_validator_by_type(validators,PublicationArtigoValidator)
        publicationCapituloLivroValidator = self.retrieve_validator_by_type(validators,PublicationCapituloLivroValidator)
        publicationDOIValidator = self.retrieve_validator_by_type(validators,PublicationDOIValidator)
        publicationEventosValidator = self.retrieve_validator_by_type(validators,PublicationEventosValidator)
        publicationFormacaoValidator = self.retrieve_validator_by_type(validators,PublicationFormacaoValidator)
        publicationLivrosValidator = self.retrieve_validator_by_type(validators, PublicationLivrosValidator)
        publicationORCIDValidator = self.retrieve_validator_by_type(validators, PublicationORCIDValidator)
        publicationOrientacoesValidator = self.retrieve_validator_by_type(validators,PublicationOrientacoesValidator)
            
        
        # Relacionamento com cursos
        transformed_records = []

        for record_string in records:
            try:
                if record_string == None or len(record_string.strip()) == 0:
                    continue
                
                PUBLICATION_TYPE = None

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

                palavras_chave  = self.get_field_value(record, "topic")
                record_node_publishDate = self.get_field_value(record, "publishDate")
                record_node_format = self.get_field_value(record, "format")
                
                # <field name="identifier.brcris" description="hash gerado com título + ano de publicação + tipo"/>
                part1 = self.get_field_value(record, "title")
                if validar_titulo(part1) == False:
                    continue

                part2 = None
                if record_node_publishDate is not None:
                    if len(record_node_publishDate) > 0:
                        part2 = record_node_publishDate[0]
                
                if part2 is None:
                    continue

                part3 = None
                if record_node_format is not None:
                    if len(record_node_format) > 0:
                        part3 = record_node_format[0]

                if part3 is None:
                    continue

                    print(part3)
                if  part3 != '' and part3 != 'article' and part3 != 'masterThesis'   and part3 != 'doctoralThesis'  and part3 != 'dataset'  and part3 != 'report' and part3 != 'bachelorThesis' and part3 != 'review' and part3 != 'book'and part3 != 'conferenceObject':
                    print(part3)
                
                PUBLICATION_TYPE = PublicationTypeMapping.get_brcris_type(source_name='OASIS',source_type=str(part3).strip())
                if PUBLICATION_TYPE is None:
                        continue

                brcris_id_v1 = brcrisid_generator(part1,str(part2),PUBLICATION_TYPE)
                brcris_id_v2 = brcrisid_generator(part1,str(part2),PUBLICATION_TYPE,useReplaceHtmlChars=True)

                # Realiza as validações
                is_publication_valid = False
                id_validated = None

                # Tipo artigo
                if (is_publication_valid == False) and (publicationArtigoValidator is not None):
                    is_publication_valid, id_validated = publicationArtigoValidator.is_valid(f"brcris::{brcris_id_v1}")
                # Capitulo de livro
                if (is_publication_valid == False) and (publicationCapituloLivroValidator is not None):
                    is_publication_valid, id_validated = publicationCapituloLivroValidator.is_valid(f"brcris::{brcris_id_v1}")
                # DOI
                if (is_publication_valid == False) and (publicationDOIValidator is not None):
                    is_publication_valid, id_validated = publicationDOIValidator.is_valid(f"brcris::{brcris_id_v1}")
                # Eventos
                if (is_publication_valid == False) and (publicationEventosValidator is not None):
                    is_publication_valid, id_validated = publicationEventosValidator.is_valid(f"brcris::{brcris_id_v1}")
                # Formacao
                if (is_publication_valid == False) and (publicationFormacaoValidator is not None):
                    is_publication_valid, id_validated = publicationFormacaoValidator.is_valid(f"brcris::{brcris_id_v1}")
                # Livros
                if (is_publication_valid == False) and (publicationLivrosValidator is not None):
                    is_publication_valid, id_validated = publicationLivrosValidator.is_valid(f"brcris::{brcris_id_v1}")
                # ORCID
                if (is_publication_valid == False) and (publicationORCIDValidator is not None):
                    is_publication_valid, id_validated = publicationORCIDValidator.is_valid(f"brcris::{brcris_id_v1}")
                # Orientações
                if (is_publication_valid == False) and (publicationOrientacoesValidator is not None):
                    is_publication_valid, id_validated = publicationOrientacoesValidator.is_valid(f"brcris::{brcris_id_v1}")
                
                if is_publication_valid == False:
                    continue
                

                publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}"))
                publication_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
                if brcris_id_v1 != brcris_id_v2:
                    publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v2}v2"))
                    publication_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v2}v2"))
        
                # <field name="identifier.doi" description="id doi"/>
                # TODO


                #<field name="identifier.capes" description="id capes"/>
                # TODO

                # <field name="identifier.bdtd"/>
                # TODO

                # <field name="identifier.oasisbr"/>
                oasisbr = self.get_field_value(record, "id")
                if oasisbr is not None and oasisbr.strip() != "":
                    publication_SemanticIdentifiers_tupla.append(("oasisbr", f"oasisbr::{oasisbr}"))
                    publication_fields_identifier_tupla.append(("identifier.oasisbr", oasisbr))

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
                # TODO

                # <field name="title"/> <!-- testar api de padronizacao do Rene -->
                # TODO
                
                # <field name="subtitle"/>
                # TODO

                # <field name="alternativeTitle"/>
                # TODO
                
                # <field name="defenceDay"/> <!-- somente ano -->
                # TODO

                # <field name="publicationDate"/> <!-- somente ano -->
                # TODO

                # <field name="degreeDate"/>
                # TODO

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
                # TODO

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
                # TODO		

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

                        publication_fields_tupla.append(("keyword", nbr_title(palavra_chave)))

                
                # <field name="abstract"/>
                publication_abstract = self.get_field_value(record, "description")
                publication_fields_tupla.append(("abstract",  trata_string(publication_abstract)))

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
                
                transformed_records.append(new_record)
            except Exception as e:
                logger.error(f"Falha ao processo objeto de formação da Plataforma lattes e converter em publicação. Registro {record_string}", exc_info=True)
        return transformed_records

    