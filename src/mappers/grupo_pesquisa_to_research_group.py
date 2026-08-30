import json
from logging import Logger
from typing import List
from validators.orgunit_validator import OrgUnitValidator
from util.text_validator import validar_titulo
from util.helper_nbr_rene import nbr_title
from validators.base_validator import BaseValidator
from util.unique_identifier_generator import brcrisid_generator
from util.text_transformers import trata_string
from .base_mapper import BaseMapper


class GrupoPesquisaResearchGroupMapper(BaseMapper):
    def get_source(self) -> str:
        return "CNPQ"

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

        for record_item in records:
            if (record_item == None) or (record_item == "") or (len(record_item) == 0):
                continue
            
            indice_dict = None
            grupo_dict = None
            recursos_humanos_dict = None

            for arquivo in record_item['arquivos']:
                if arquivo == 'indice.json':
                    with open(f"{record_item['pasta_atual']}/{arquivo}", 'r', encoding='utf-8') as arq:
                        indice_dict =json.load(arq)
                if arquivo == 'grupo.json':
                    with open(f"{record_item['pasta_atual']}/{arquivo}", 'r', encoding='utf-8') as arq:
                        grupo_dict =json.load(arq)
                if arquivo == 'recursos_humanos.json':
                    with open(f"{record_item['pasta_atual']}/{arquivo}", 'r', encoding='utf-8') as arq:
                        recursos_humanos_dict =json.load(arq)

            if grupo_dict is None:
                continue
            
            # Identificador semanticos 
            grupo_SemanticIdentifiers_tupla = []
            # Campos Identificador
            grupo_fields_identifier_tupla = []
            # Campos field
            grupo_fields_tupla = []
            
            # Gerando a referência deste registro para relacionamentos
            grupo_ref = self.creat_ref_identifier()

            print(f"Processando registro: {grupo_ref}")

            # Ignorar grupos excluídos
            situacao_grupo = self.__get_key_value_in_section(grupo_dict["secoes"],"identificação", "Situação do grupo")
            if situacao_grupo == 'Excluído':
                continue

            # <field name="identifier.brcris" description="baseado no nome do grupo + ano de criação"/>
            part1 = self.get_field_value(grupo_dict, "nome")
            if validar_titulo(part1) == False:
                continue
            part2 =  self.__get_key_value_in_section( grupo_dict["secoes"],"identificação","Ano de formação")
            if part2 is None:
                continue

            

            brcris_id_v1 = brcrisid_generator(part1,str(part2))
            brcris_id_v2 = brcrisid_generator(part1,str(part2),useReplaceHtmlChars=True)

            grupo_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v1}"))
            grupo_fields_identifier_tupla.append(("identifier.brcris", brcris_id_v1))
            if brcris_id_v1 != brcris_id_v2:
                grupo_SemanticIdentifiers_tupla.append(("brcris", f"brcris::{brcris_id_v2}v2"))
                grupo_fields_identifier_tupla.append(("identifier.brcris", f"{brcris_id_v2}v2"))
    
            # <field name="identifier.dgp" description="codigo do dgp do grupo no CNPq"/>
            identifier_dgp = self.get_field_value(grupo_dict, "id")
            if self.has_value(identifier_dgp):
                grupo_fields_identifier_tupla.append(("identifier.dgp", identifier_dgp))

            
            # <field name="name" description="nome do grupo"/>
            grupo_nome = self.get_field_value(grupo_dict, "nome")
            if self.has_value(grupo_nome):
                grupo_nome = nbr_title(grupo_nome)
                grupo_fields_tupla.append(("name", grupo_nome))

            # <field name="description" description="resumo informado do grupo"/>
            # TODO

            # <field name="status" />
            grupo_status = self.__get_key_value_in_section(grupo_dict["secoes"],"identificação", "Situação do grupo")
            if self.has_value(grupo_status):
                grupo_fields_tupla.append(("status", grupo_status))

            # <field name="creationYear" description="ano de criação do grupo"/>
            grupo_creationYear = self.__get_key_value_in_section(grupo_dict["secoes"],"identificação", "Ano de formação")
            if self.has_value(grupo_creationYear):
                grupo_fields_tupla.append(("creationYear", grupo_creationYear))
            
            # <field name="URL" description="URL de acesso ao grupo"/>
            grupo_URL = self.get_field_value(grupo_dict, "url")
            if self.has_value(grupo_URL):
                grupo_fields_tupla.append(("URL", grupo_URL))

            # <field name="researchLine" description="nome da linha de pesquisa do grupo (pode-se ter várias)"/> <!-- somente capitalizar e remover duplicadas -->
            grupo_researchLines = self.__get_researchLines(grupo_dict)
            for rl in grupo_researchLines:
                grupo_fields_tupla.append(("researchLine", rl))

            # <field name="keyword" description="palavras chaves informadas do grupo (pode-se ter várias)"/> <!-- somente capitalizar e remover duplicadas -->
            # TODO

            # <field name="knowledgeArea" description="área de conhecimento do grupo(pode-se ter várias)"/> <!-- nao precisa validar na lista de autoridade, mas deve ser captalizado corretamente. Deve concatenar toda a árvore em uma estrutura de diretorios. Ex.: Grande Area / Area / Sub-area / Especialidade -->
            grupo_knowledgeArea = self.__get_key_value_in_section(grupo_dict["secoes"],"identificação", "Área predominante")
            if self.has_value(grupo_knowledgeArea):
                grupo_knowledgeArea = grupo_knowledgeArea.replace(";"," /")
                grupo_fields_tupla.append(("knowledgeArea", grupo_knowledgeArea))

            # <field name="applicationSector" description="setor de aplicação do grupo (pode-se ter várias)"/><!-- somente capitalizar e remover duplicadas -->
            # TODO

            # <field name="equipment" description="equipamentos que estão associados ao grupo"/><!-- somente capitalizar e remover duplicadas -->
            grupo_equipment = self.__get_equipment(grupo_dict)
            for eq in grupo_equipment:
                grupo_fields_tupla.append(("equipment", eq))

            # <field name="software" description="softwares que estão disponíveis ao grupo"/><!-- somente capitalizar e remover duplicadas -->
            grupo_software = self.__get_software(grupo_dict)
            for sf in grupo_software:
                grupo_fields_tupla.append(("software", sf))
            

            # Monta a estrutura que o XMLWriter espera
            new_entity_research_group = {
                "entity_attribs": {
                    "type": "ResearchGroup",
                    "ref": grupo_ref
                },
                "semantic_identifiers":[
                    {"name": name, "value": value} for name, value in grupo_SemanticIdentifiers_tupla if value is not None
                ],
                "fields_identifier": [
                    {"name": name, "value": value} for name, value in grupo_fields_identifier_tupla if value is not None
                ],
                "fields": [
                    {"name": name, "value": value} for name, value in grupo_fields_tupla if value is not None
                ]
            }

            new_record = {
                "entities": [new_entity_research_group],
                "relations":[]
            }

            # 01 - Lideres do grupo
            # <relation name="LeaderResearchGroup" description="Is a relation between the Leader Person and ResearchGroup" fromEntity="Person" toEntity="ResearchGroup">
            #     <field name="scholarshipHolder" description="Indicates if the member is a scholarship holder"/>
            # </relation>
            lidres_ja_relacionados = []
            nomes_lideres = self.__get_key_value_in_section(grupo_dict["secoes"],"identificação", "Líder(es) do grupo")
            if self.has_value(nomes_lideres):
                nomes_lideres = nomes_lideres.replace(" ui-button","")
                lista_nomes_lideres = nomes_lideres.split(";")
                for nome_lider in lista_nomes_lideres:
                    nome_lider = nome_lider.strip()
                    lattes_id = self.__get_lattes_id(recursos_humanos_dict,nome_lider)

                    new_person, person_ref = self.__transform_person(nome_lider,lattes_id)
                    if not new_person is None:
                        lidres_ja_relacionados.append(lattes_id)
                        new_relation = {
                            "type": "LeaderResearchGroup",
                            "fromEntityRef": person_ref, # fromEntity="Person"
                            "toEntityRef":  grupo_ref, # toEntity="ResearchGroup"
                        } 
                        new_record["relations"].append(new_relation)
                        new_record["entities"].append(new_person)
                    

            # 02 - Pesquisadores membros do grupos
            # <relation name="MemberResearchGroup" description="Is a relation between Person and ResearchGroup" fromEntity="Person" toEntity="ResearchGroup">
            #     <field name="role" description="Indicate the rold of the member"/>
            #     <field name="scholarshipHolder" description="Indicates if the member is a scholarship holder"/>
            # </relation>
            nomes_membros = self.__get_pesquisador(grupo_dict)
            for nome_membro in nomes_membros:
                lattes_id = self.__get_lattes_id(recursos_humanos_dict,nome_membro)
                new_person, person_ref = self.__transform_person(nome_membro,lattes_id)
                if not new_person is None:
                    # cargo = None
                    # if lattes_id in lidres_ja_relacionados:
                    #     cargo = "Líder"
                    
                    new_relation = {
                            "type": "MemberResearchGroup",
                            "fromEntityRef": person_ref, # fromEntity="Person"
                            "toEntityRef":  grupo_ref, # toEntity="ResearchGroup"
                            # "attributes":[
                            #     {"name": "role", "value": cargo} if cargo is not None else None
                            # ]
                        } 
                    new_record["relations"].append(new_relation)
                    new_record["entities"].append(new_person)
            
            # 03 - OrgUnit dona do grupo
            # <relation name="LeaderResearchGroupOrgUnit" description="The OrgUnit(s) that provided the ResearchGroup leader." fromEntity="OrgUnit" toEntity="ResearchGroup"/>
            nomes_orgunit_lideres = self.__get_key_value_in_section(grupo_dict["secoes"],"identificação", "Instituição do grupo")
            nomes_orgunit_lideres = nomes_orgunit_lideres.split(";")
            for nome_orgunit in nomes_orgunit_lideres:
                nome_orgunit = nome_orgunit.split('-')[0].strip()
                new_orgunit, orgunit_ref = self.__transform_orgunit(nome_orgunit, orgunit_validator)
                if not new_orgunit is None:
                    new_relation = {
                        "type": "LeaderResearchGroupOrgUnit",
                        "fromEntityRef": orgunit_ref, # fromEntity="OrgUnit"
                        "toEntityRef":  grupo_ref, # toEntity="ResearchGroup"
                    } 
                    new_record["relations"].append(new_relation)
                    new_record["entities"].append(new_orgunit)
            

            # 04 - OrgUnit parceiras do grupo
            # <relation name="PartnerResearchGroupOrgUnit" description="The OrgUnits(s) that have Partner with the ResearchGroups" fromEntity="OrgUnit" toEntity="ResearchGroup"/>
            nomes_orgunit_parceiras = self.__get_instituicoes_parceiras(grupo_dict)
            for nome_orgunit in nomes_orgunit_parceiras:
                new_orgunit, orgunit_ref = self.__transform_orgunit(nome_orgunit, orgunit_validator)
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

    def __transform_person(self, nome, lattes_id) -> tuple[dict, str]:
        """
        Converte registros  de autores  
        """
        author_SemanticIdentifiers_tupla = []
        author_fields_identifier_tupla = []
        author_fields_tupla = []

        if lattes_id is None:
            return None, None
        
        if nome:
            author_fields_tupla.append(("name", nome))
        

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

    
    def __get_key_value_in_section(self, dicionario, section, chave):
        # Itera por todas as seções dentro da lista "secoes"
        for secao in dicionario:
            if secao["titulo"].lower() == section:
                valor = secao["campos"][chave]

                if valor == None:
                    return None
                
                if valor is str:
                    if valor == '':
                        return None
                    
                    if str(valor).strip().lower() == 'null':
                        return None
                    
                return valor
        return None
    
    def __get_researchLines(self, dicionario):
        retorno = []
        # Itera por todas as seções dentro da lista "secoes"
        for secao in dicionario['secoes']:
            if secao["titulo"].lower() == "linhas de pesquisa":
                for tabela in secao['tabelas']:
                    for registro in tabela['registros']:
                        linha = registro["Nome da linha de pesquisa"]
                        if linha:
                            linha = nbr_title(linha)
                            retorno.append(linha)
        return list(set(retorno)) 
    
    def __get_equipment(self, dicionario):
        retorno = []
        # Itera por todas as seções dentro da lista "secoes"
        for secao in dicionario['secoes']:
            if secao["titulo"].lower() == "equipamentos e softwares relevantes":
                for tabela in secao['tabelas']:
                    if 'Equipamentos' in tabela['cabecalhos']:
                        for registro in tabela['registros']:
                            equipamento = registro["Equipamentos"]
                            if equipamento:
                                retorno.append(equipamento)
        return list(set(retorno)) 
    
    def __get_software(self, dicionario):
        retorno = []
        # Itera por todas as seções dentro da lista "secoes"
        for secao in dicionario['secoes']:
            if secao["titulo"].lower() == "equipamentos e softwares relevantes":
                for tabela in secao['tabelas']:
                    if 'Softwares' in tabela['cabecalhos']:
                        for registro in tabela['registros']:
                            software = registro["Softwares"]
                            if software:
                                retorno.append(software)
        return list(set(retorno)) 
    
    def __get_lattes_id(self, dicionario, nome: str):
        lattes_id = None
        for pesquisador in dicionario['categorias']['pesquisadores']:
            if pesquisador["nome"].lower() == nome.lower():
                lattes_id = pesquisador["id_lattes"]
                if lattes_id:
                    break
        if lattes_id is None:
            for estudante in dicionario['categorias']['estudantes']:
                if estudante["nome"].lower() == nome.lower():
                    lattes_id = estudante["id_lattes"]
                    if lattes_id:
                        break
        
        if lattes_id is None:
            for tecnico in dicionario['categorias']['tecnicos']:
                if tecnico["nome"].lower() == nome.lower():
                    lattes_id = tecnico["id_lattes"]
                    if lattes_id:
                        break

        return lattes_id
    
    def __get_pesquisador(self, dicionario):
        retorno = []
        # Itera por todas as seções dentro da lista "secoes"
        for secao in dicionario['secoes']:
            if secao["titulo"].lower() == "recursos humanos":
                for tabela in secao['tabelas']:
                    for registro in tabela['registros']:
                        nome = None
                        if "Pesquisadores" in registro:
                            nome = registro["Pesquisadores"]
                        elif "Estudantes" in registro:
                            nome = registro["Estudantes"]
                        elif "Técnicos" in registro:
                            nome = registro["Técnicos"]
                        
                        if nome:
                            retorno.append(nome)
        return list(set(retorno)) 
    
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
    

    def __get_instituicoes_parceiras(self, dicionario):
        retorno = []
        # Itera por todas as seções dentro da lista "secoes"
        for secao in dicionario['secoes']:
            if secao["titulo"].lower() == "instituições parceiras relatadas pelo grupo":
                for tabela in secao['tabelas']:
                    for registro in tabela['registros']:
                        nome = registro["Nome da Instituição Parceira"]
                        if nome:
                            retorno.append(nome)
        return list(set(retorno)) 
           