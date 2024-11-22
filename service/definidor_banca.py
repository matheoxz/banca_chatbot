import streamlit as st
from langchain_chroma import Chroma
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI

from domain.enums import ModelEnum
from domain.responses_models import ListaPalavrasChave, ListaVariacoesTitulo, ListaProfessores, Professor, ListaRelevanciaProfessores

def define_banca(titulo: str, resumo: str, palavras_chave: str, modelo: ModelEnum, vector_store: Chroma): 

    match modelo:
        case ModelEnum.CHATGPT.value:
            llm = ChatOpenAI(model="gpt-4o-mini")
        case ModelEnum.GEMINI.value:
            llm = ChatVertexAI(model="gemini-1.5-flash-001")

    with st.status("Definindo banca", expanded=True):
        palavras_chave_extraidas_titulo = extrai_palavraschave_titulo(titulo, resumo, llm)
        set_palavraschave = set(palavras_chave_extraidas_titulo.palavras_chave).union(set(palavras_chave.split(";")))

        variacoes_titulo = gera_variacoes_titulo(titulo, resumo, set_palavraschave, llm)
        variacoes_titulo.titulos.extend([titulo, resumo])

        lista_professores = procura_professores(vector_store, set_palavraschave, variacoes_titulo).ordena_por_relevancia()
        
        lista_professores_final = checa_relevancia(resumo, llm, set_palavraschave, variacoes_titulo, lista_professores)

        st.write("Sugestão de Banca definida!")
    
    return lista_professores_final

def checa_relevancia(resumo, llm, set_palavraschave, variacoes_titulo, lista_professores: ListaProfessores) -> list[Professor]:
    st.write("Checando relevância dos professores encontrados...")
    contextualize_q_system_prompt = f'''
            Você é um sistema assistente de definição de bancas de mestrado.
            Você recebe uma lista de possíveis títulos para um trabalho de mestrado,  o seu resumo e uma lista de palavras chave que descrevem a área de pesquisa e objetivos.
            Você receberá uma lista de professores que podem ser candidatos a avaliar o trabalho de mestrado, você deve dizer se cada professor é relevante ou não para o trabalho no campo "relevancia" através de um booleano
            Para cada professor você deve fornecer uma justificativa para a sua relevância ou falta de relevância com o trabalho de mestrado, em um parágrafo de texto, citando as áreas de pesquisa relevantes do professor.
            Os professores devem ser escolhidos de acordo com a familiaridade com algum dos temas tratados no trabalho de mestrado.
            Titulos: {variacoes_titulo.titulos}
            Resumo: {resumo}
            Palavras-chave: {set_palavraschave}
        '''
    structured_llm = llm.with_structured_output(ListaRelevanciaProfessores)

    lista_relevancia = ListaRelevanciaProfessores()
    lista_professores_ = lista_professores.professores
    for id in range(0, len(lista_professores_), 5):
        id_final = lambda x: x+5 if x+5 < len(lista_professores_) else len(lista_professores_)
        cinco_professores = lista_professores_[id: id_final(id)]
        cinco_professores_str = "\n".join([("{" + f'"nome":"{professor.nome}", "resumo": "{professor.resumo}", "linhas_pesquisa": "{professor.linhas_pesquisa}"' + "}") for professor in cinco_professores])
        resposta = structured_llm.invoke(contextualize_q_system_prompt + f"\nProfessores: {cinco_professores_str}")
        lista_relevancia.add_relevancias(resposta.relevancia_professores)
    
    for professor in lista_professores_:
        professor_na_lista = next((p for p in lista_relevancia.relevancia_professores if p.nome == professor.nome), None)
        if professor_na_lista is not None:
            professor.relevante = professor_na_lista.relevante
            professor.justificativa_relevancia = professor_na_lista.justificativa
        else:
            print(f"Professor {professor.nome} não encontrado na lista de relevância")
    st.write(f"{sum(1 for p in lista_professores_ if p.relevante)} professores relevantes encontrados!")

    return lista_professores_

def define_relevancia_professores(lista_professores, contextualize_q_system_prompt, structured_llm):
    
    return lista_professores

def procura_professores(vector_store: Chroma, set_palavraschave: set, variacoes_titulo: ListaVariacoesTitulo) -> ListaProfessores:
    st.write("Procurando professores relevantes...")
    lista_professores = ListaProfessores(professores=[])
    for titulo in variacoes_titulo.titulos:
        cinco_professores_mais_proximos = vector_store.similarity_search_with_relevance_scores(f"{titulo} {set_palavraschave}", k=5)
        lista_professores.add_professores([Professor.from_tuple_json_similarity(professor) for professor in cinco_professores_mais_proximos])
    st.write(f"{len(lista_professores.professores)} Professores encontrados!")
    return lista_professores

def extrai_palavraschave_titulo(titulo: str, resumo:str, llm: BaseChatModel) ->  ListaPalavrasChave:
    theme_extractor_prompt = f'''
        A partir do título "{titulo}" e do resumo abaixo, extraia as áreas de pesquisa do trabalho de mestrado.
        Resumo: {resumo}
        Tente responder às perguntas a seguir com base no título e resumo fornecidos:
            - O trabalho é de qual área do conhecimento? Qual curso de graduação é mais próximo do tema?
            - Quais são os principais objetivos do trabalho? Quais as palavras chave que descrevem o tema geral do trabalho?
            - O que o trabalho se propõe a pesquisar? Qual pergunta ele tenta responder?
    '''
    st.write("Extraindo áreas de pesquisa do título...")
    structured_llm = llm.with_structured_output(ListaPalavrasChave)
    resposta = structured_llm.invoke(theme_extractor_prompt)
    st.write(f"Palavras-chave a partir do título e resumo")
    st.write(resposta.palavras_chave)

    return resposta

def gera_variacoes_titulo(titulo: str, resumo:str, palavraschave: set, llm: BaseChatModel) -> ListaVariacoesTitulo:
    theme_extractor_prompt = f'''
        Sugira 5 novos títulos para o trabalho de mestrado com título {titulo} e palavras chave {palavraschave}.
        Resumo: {resumo}
        Tente destacar algumas palavras-chaves no título e use-as como base para gerar novas variações, combinando-as de deiversas formas.
    '''
    st.write("Variando título...")
    structured_llm = llm.with_structured_output(ListaVariacoesTitulo)
    resposta = structured_llm.invoke(theme_extractor_prompt)
    st.write(f"Titulos para mestrado: ")
    st.write(resposta.titulos)

    return resposta