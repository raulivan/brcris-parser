import json
from typing import List
from validators.base_validator import BaseValidator
from util.extracao import extrair_id_openalex
from util.unique_identifier_generator import brcrisid_generator
from util.text_transformers import capitalizar_nome, translate_language, translate_type_of_publication, trata_string
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
            
            
            
             
            #<field name="identifier.brcris" description="hash gerado com título + ano de publicação + tipo"/>
            part1 = self.get_field_value(record, "title")
            part2 = self.get_field_value(record, "publication_year")
            part3 = translate_type_of_publication(self.get_field_value(record, "type"))

            brcris_id_v1 = brcrisid_generator(part1,part2,part3)
            brcris_id_v2 = brcrisid_generator(part1,part2,part3,useReplaceHtmlChars=True)

            publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}"))
            publication_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
            if brcris_id_v1 != brcris_id_v2:
                publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v2}v2"))
                publication_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v2}v2"))
    
            # <field name="identifier.doi" description="id doi"/>
            doi_fora = self.get_field_value(record, "doi")
            publication_SemanticIdentifiers_tupla.append(("doi", f"doi::{doi_fora}"))
            publication_fields_identifier_tupla.append(("identifier.doi", doi_fora))
            doi_ids = self.get_field_value(record_node_ids, "doi")
            if doi_fora != doi_ids:
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
            publication_fields_identifier_tupla.append(("identifier.other", id_open_alex))
            id_open_alex_ids = self.get_field_value(record_node_ids, "id")
            if id_open_alex != id_open_alex_ids:
                publication_fields_identifier_tupla.append(("identifier.other", id_open_alex_ids))

            # <field name="type"/> <!-- validar na lista de autoridade de tipos e gravar no idima PT (anteriormente era no coar)-->
            publication_type = translate_type_of_publication(self.get_field_value(record, "type"))
            publication_fields_tupla.append(("type", publication_type))

            # <field name="language"/> <!-- validar na lista de autoridade de idiomas e gravar no idima PT -->
            publication_language = translate_language(self.get_field_value(record, "language"))
            publication_fields_tupla.append(("language", publication_language))

            # <field name="title"/> <!-- testar api de padronizacao do Rene -->
            publication_title = self.get_field_value(record, "title")
            if publication_title is not None:
                publication_title = capitalizar_nome(publication_title)
                publication_fields_tupla.append(("title", publication_title))
			
            # <field name="subtitle"/>
            # TODO

            # <field name="alternativeTitle"/>
            publication_alternative_title = self.get_field_value(record, "display_name")
            if publication_alternative_title is not None:
                publication_alternative_title = capitalizar_nome(publication_alternative_title)
                if publication_alternative_title != publication_title:
                    publication_fields_tupla.append(("alternativeTitle", publication_alternative_title))
            
            # <field name="defenceDay"/> <!-- somente ano -->
            # TODO

            # <field name="publicationDate"/> <!-- somente ano -->
            publication_publicationDate = self.get_field_value(record, "publication_year")
            publication_fields_tupla.append(("publicationDate", publication_publicationDate))

            # <field name="degreeDate"/>
            # TODO

            # <field name="number"/>
            # TODO

            # <field name="issue"/>
            publication_issue = self.get_field_value(record_node_biblio, "issue")
            publication_fields_tupla.append(("issue", publication_issue))
            
            
            # <field name="volume"/>
            publication_volume= self.get_field_value(record_node_biblio, "volume")
            publication_fields_tupla.append(("volume", publication_volume))

            # <field name="series"/>
            # TODO

            # <field name="edition"/>
            # TODO

            # <field name="startPage"/>
            publication_startPage = self.get_field_value(record_node_biblio, "first_page")
            publication_fields_tupla.append(("startPage", publication_startPage))

            # <field name="endPage"/>
            publication_endPage = self.get_field_value(record_node_biblio, "last_page")
            publication_fields_tupla.append(("endPage", publication_endPage))

            # <field name="author"/>
            for autor in record_node_authorships:
                autor_name = self.get_field_value(autor, "author.display_name")
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
            publication_fields_tupla.append(("resourceUrl", publication_resourceUrl_1))

            publication_resourceUrl_2 = self.get_field_value(record_node_primary_location, "pdf_url")
            publication_fields_tupla.append(("resourceUrl", publication_resourceUrl_2))
			

            # <field name="rights"/>
            # TODO

            # <field name="license"/>
            publication_license = self.get_field_value(record_node_primary_location, "license")
            publication_fields_tupla.append(("license", publication_license))

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

            # PAREI AUQI FALTA REVISAR PRA BAIXO
	

			
			
			
			

			
			
			

            
			

            












            if publication_name is not None:
                publication_name = capitalizar_nome(publication_name)
                publication_fields_tupla.append(("title", publication_name))
			

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
                    
                    publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}"))
                    publication_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
                    if brcris_id_v1 != brcris_id_v2:
                        publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}v2"))
                        publication_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v1}v2"))

                    publication_SemanticIdentifiers_tupla.append(("issn", f"issn::{item_issn_sem_espacos}"))
                    publication_fields_identifier_tupla.append(("identifier.issn", item_issn_sem_espacos))

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
                                    
                                    publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}"))
                                    publication_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
                                    if brcris_id_v1 != brcris_id_v2:
                                        publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}v2"))
                                        publication_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v1}v2"))

                                    publication_SemanticIdentifiers_tupla.append(("issn", f"issn::{item_issn_sem_espacos}"))
                                    publication_fields_identifier_tupla.append(("identifier.issn", item_issn_sem_espacos))
                            else:
                                if self.has_value(item_ids_value):
                                                            
                                    item_issn_sem_espacos = trata_string(item_ids_value)
                            
                                    brcris_id_v1 = brcrisid_generator(item_issn_sem_espacos)
                                    brcris_id_v2 = brcrisid_generator(item_issn_sem_espacos,useReplaceHtmlChars=True)
                                    
                                    publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}"))
                                    publication_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
                                    if brcris_id_v1 != brcris_id_v2:
                                        publication_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}v2"))
                                        publication_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v1}v2"))

                                    publication_SemanticIdentifiers_tupla.append(("issn", f"issn::{item_issn_sem_espacos}"))
                                    publication_fields_identifier_tupla.append(("identifier.issn", item_issn_sem_espacos))
                                
            #********************** <field name="identifier.issn_l" description="ISSN-L"/>
            if self.has_value(record_node_ids):
                for item_ids_key, item_ids_value  in record_node_ids.items():
                    if item_ids_key == 'issn_l':
                        if isinstance(item_ids_value, list):
                            for item_issnl in item_ids_value:
                                if not self.has_value(item_issnl):
                                    continue
                                publication_fields_identifier_tupla.append(("identifier.issn_l", trata_string(item_issnl)))
                        else:
                            if self.has_value(item_ids_value):
                                publication_fields_identifier_tupla.append(("identifier.issn_l", trata_string(item_ids_value)))

            #********************** <field name="identifier.openalex" description="Identificação da revista na OpenAlex"/>
            if self.has_value(record_node_ids):
                for item_ids_key, item_ids_value  in record_node_ids.items():
                    if item_ids_key == 'openalex':
                        if not self.has_value(item_ids_value):
                             continue
                        publication_fields_identifier_tupla.append(("identifier.openalex", extrair_id_openalex(trata_string(item_ids_value))))
                        publication_SemanticIdentifiers_tupla.append(("openalex", f"openalex::{extrair_id_openalex(trata_string(item_ids_value))}"))
                        
   
            #********************** <field name="title" description="título da revista"/> <!-- testar api de padronizacao do Rene?? -->
            
            
            publication_display_name = self.get_field_value(record, "display_name")
            if publication_display_name is not None:
                publication_display_name = capitalizar_nome(publication_display_name)
                publication_fields_tupla.append(("title", publication_display_name))
            
            json_node_alternate_titles =  self.get_field_value(record, 'alternate_titles')
            if self.has_value(json_node_alternate_titles):
                for item in json_node_alternate_titles:
                    if item is not None:
                        publication_alternative_name = capitalizar_nome(item)
                        publication_fields_tupla.append(("title", publication_alternative_name))
                        
            #********************** <field name="publisher" description="Quem publica a revista"/> <!-- testar api de padronizacao do Rene?? -->
            json_node_publisher_nome = self.get_field_value(record, 'publisher')
            if self.has_value(json_node_publisher_nome):
                publisher_name = capitalizar_nome(json_node_publisher_nome)
                publication_fields_tupla.append(("publisher", publisher_name))
                
            #********************** <field name="websiteURL" description="url da revista"/>
            json_node_homepage_url = self.get_field_value(record, 'homepage_url')
            if self.has_value(json_node_homepage_url):
                publication_fields_tupla.append(("websiteURL", trata_string(json_node_homepage_url)))
                

            #********************** <field name="isOa" description="Verifica se a revista é Oa (True ou False)"/>
            json_node_is_oa = self.get_field_value(record, 'is_oa')
            if self.has_value(json_node_is_oa):
                publication_fields_tupla.append(("isOa", str(json_node_is_oa)))
                
            
            #********************** <field name="isInDoaj" description="Verifica se a revista está no Doaj (True ou False)"/>
            json_node_is_in_doaj = self.get_field_value(record, 'is_in_doaj')
            if  self.has_value(json_node_is_in_doaj):
                publication_fields_tupla.append(("isInDoaj", str(json_node_is_in_doaj)))
            
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
                    publication_fields_tupla.append(("apcCost", apcCost))
                    
            
            #********************** <field name="countryCode" description="Código do país"/>
            json_node_country_code =  self.get_field_value(record, 'country_code')
            if self.has_value(json_node_country_code):
                publication_fields_tupla.append(("countryCode", trata_string(json_node_country_code)))
            
            #********************** <field name="type" description="Tipo de publicação"/>
            json_node_type = self.get_field_value(record, 'type')
            if self.has_value(json_node_type):
                publication_fields_tupla.append(("type", trata_string(json_node_type)))
                
            #********************** <field name="assessmentArea" description="Área da Revista"/>
            json_node_areas_avaliacao = self.get_field_value(record, 'areas_avaliacao')
            if self.has_value(json_node_areas_avaliacao):
                for item in json_node_areas_avaliacao:
                    publication_fields_tupla.append(("assessmentArea", trata_string(item)))
            
            #********************** <field name="qualis" description="Qualis da Revista"/>
            json_node_estrato = self.get_field_value(record, 'estrato')
            if self.has_value(json_node_estrato):
                publication_fields_tupla.append(("qualis", trata_string(json_node_estrato)))
            
            #********************** <field name="keywords" description="Palavras chave "/> <!-- testar api de padronizacao do Rene?? -->
            # NÃO TEM
            
            #********************** <field name="2yr_mean_citedness" description="média de citação"/>
            json_node_summary_stats = self.get_field_value(record, 'summary_stats')
            if self.has_value(json_node_summary_stats) :
                summary_stats = self.get_field_value(json_node_summary_stats, '2yr_mean_citedness')
                if self.has_value(summary_stats) :
                    publication_fields_tupla.append(("2yr_mean_citedness", str(summary_stats)))
            
            
            #********************** <field name="h_index" description="índice h"/>
            if self.has_value(json_node_summary_stats) :
                h_index = self.get_field_value(json_node_summary_stats,'h_index')
                if self.has_value(h_index) :
                    publication_fields_tupla.append(("h_index", str(h_index))) 
                    
            #********************** <field name="i10_index" description="índice i10"/>
            if self.has_value(json_node_summary_stats) :
                i10_index = self.get_field_value(json_node_summary_stats,'i10_index')
                if self.has_value(i10_index) :
                    publication_fields_tupla.append(("i10_index", str(i10_index))) 
                    
            #********************** <field name="googleH5" description="Google Scholar H5"/>
            
            
            new_entity_journal = {
                "entity_attribs": {
                    "type": "Journal",
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
            
            # Monta a estrutura que o XMLWriter espera
            new_record = {
                "entities": [new_entity_journal],
                "relations":[]
            }
            
            transformed_records.append(new_record)
        return transformed_records
    
    
    