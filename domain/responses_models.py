'''
Este módulo define vários modelos Pydantic para representar entidades relacionadas ao sistema de definição de bancas de mestrado. 
Estes modelos são utilizados para serializar e desserializar dados entre diferentes partes do sistema e enviados às LLMs para resposta com modelo estrturado.
'''

import ast
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain.docstore.document import Document


class ListaPalavrasChave(BaseModel):
    '''Classe que representa a lista de palavras-chave de um trabalho de mestrado'''
    palavras_chave: List[str] = Field(..., title="Lista de palavras-chave e áreas de pesquisa do trabalho de mestrado", 
                                      description="Lista de palavras-chave e áreas de pesquisa que descrevem o tema do trabalho de mestrado")
    
class ListaVariacoesTitulo(BaseModel):
    '''Classe que representa a lista de possíveis títulos de um trabalho de mestrado'''
    titulos: List[str] = Field(..., title="Lista de titulos", 
                                      description="Possíveis títulos para um trabalho de mestrado")

class ListaTraduzida(BaseModel):
    '''Class that represents a list of translated titles and keywords'''
    titulos: List[str] = Field(..., title="List of titles in English", 
                                      description="Possible titles for a master's thesis in English")
    palavras_chave: List[str] = Field(..., title="List of keywords in English", 
                                      description="List of keywords and research areas that describe the theme of the master's thesis in English")

class Professor(BaseModel):
    '''Classe que representa um professor'''
    nome: Optional[str] = Field(default=None, title="Nome do professor", description="Nome do professor")
    #uuid: Optional[str] = Field(default=None, title="UUID do professor", description="UUID do professor")
    resumo: Optional[str] = Field(default=None, title="Resumo do professor", description="Resumo do professor")
    linhas_pesquisa: Optional[List[str]] = Field(default=None, title="Área de atuação do professor", description="Área de atuação do professor")
    foto: Optional[str] = Field(default=None, title="Foto do professor", description="Foto do professor")
    lista_similaridade: Optional[List[float]] = Field(default=[], title="Similaridades do professor com o tema do trabalho de mestrado", 
                                description="Similaridades do professor com o tema do trabalho de mestrado")
    pontuacao: Optional[int] = Field(default = 0, title="Pontuação do professor", description="Em quantas pesquisas o professor foi encontrado")
    relevante: Optional[bool] = Field(default=None, title="Relevante", description="Se o professor é relevante para o trabalho de mestrado")
    justificativa_relevancia: Optional[str] = Field(default=None, title="Justificativa", description="Justificativa da relevância ou falta de relevancia do professor para o trabalho de mestrado")
    
    def from_tuple_json_similarity(data: tuple[Document, float]):
        '''Converte um dicionário em um objeto Professor'''
        try:
            dict = ast.literal_eval(data[0].page_content)
            prof = Professor(**dict)
            prof.lista_similaridade.append(data[1])
            return prof
        except Exception as e:
            print(f"Erro ao deserializar professor da base: {e}")
            print(f"Dado do professor: {data[0].page_content}")
            return Professor()
    
    def from_Document(doc: Document):
        '''Converte um Document em um objeto Professor'''
        try:
            dict = ast.literal_eval(doc.page_content)
            prof = Professor(**dict)
            return prof
        except Exception as e:
            print(f"Erro ao deserializar professor de JSON: {e}")
            print(f"Dado do professor: {doc.page_content}")
            return Professor()
        

class ListaProfessores(BaseModel):
    '''Classe que representa a lista de professores que podem avaliar um trabalho de mestrado'''
    professores: List[Professor] = Field(..., title="Lista de professores",
                                      description="Lista de professores que podem avaliar um trabalho de mestrado")
    
    def add_professor(self, professor: Professor):
        '''Adiciona um professor à lista de professores'''
        # checa se professor já existe na lista a partir do nome
        for p in self.professores:
            if p.nome == professor.nome:
                # aumenta pontuação
                p.pontuacao += 1
                # atualiza similaridade média
                p.lista_similaridade.extend(professor.lista_similaridade)
                return
        
        professor.pontuacao = 1
        professor.lista_similaridade = professor.lista_similaridade
        self.professores.append(professor)
    
    def add_professores(self, professores: List[Professor]):
        '''Adiciona uma lista de professores à lista de professores'''
        for professor in professores:
            self.add_professor(professor)
    
    def ordena_por_relevancia(self):
        '''Ordena a lista de professores por relevância'''
        self.professores.sort(key=lambda x: x.pontuacao, reverse=True)
        return self
    
class RelevanciaProfessor(BaseModel):
    '''Classe que representa a relevância do professor para um trabalho de mestrado'''
    relevante: Optional[bool] = Field(default=None, title="Relevante", description="Se o professor é relevante para o trabalho de mestrado")
    justificativa: str = Field(..., title="Justificativa", description="Justificativa da relevância ou falta de relevancia do professor para o trabalho de mestrado")
    nome: Optional[str] = Field(default=None, title="Nome", description="Professor que avalia o trabalho de mestrado")
    #uuid: Optional[str] = Field(default=None, title="UUID", description="UUID do professor que avalia o trabalho de mestrado")

class ListaRelevanciaProfessores(BaseModel):
    '''Classe que representa a lista de relevância dos professores para um trabalho de mestrado'''
    relevancia_professores: Optional[List[RelevanciaProfessor]] = Field(default=[], title="Lista de relevância dos professores",
                                                                description="Lista de relevância dos professores para um trabalho de mestrado")
    
    def add_relevancias(self, relevancia_professores: List[RelevanciaProfessor]):
        '''Adiciona uma lista de relevância dos professores à lista de relevância dos professores'''
        self.relevancia_professores.extend(relevancia_professores)