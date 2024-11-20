import json
from uuid import uuid4
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
import streamlit as st
import os

def carregaProfessores():
    load_dotenv()

    persist_directory = "data/vectorstore/profs"
    embeddings = OpenAIEmbeddings()

    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        vectordb = Chroma(collection_name="professores", persist_directory= persist_directory, embedding_function = embeddings)
    else:
        prog_bar = st.progress(0, "Carregando dados de professores...")
        try:
            professores_documentos = _carregaDocumentosJSON()
            vectordb = Chroma(collection_name="professores", persist_directory= persist_directory, embedding_function = embeddings)
            for i, doc in enumerate(professores_documentos):
                vectordb.add_documents([doc], id=str(uuid4()))
                prog_bar.progress(i/len(professores_documentos))
            prog_bar.progress(100)
        except Exception as e:
            print(e)
    return vectordb
    

def _carregaDocumentosJSON(caminho_documento = './data/json_curriculos.json'):
    with open(caminho_documento, 'r', encoding='utf-8') as file:
        lista_professores_json = json.load(file)
        
    for professor in lista_professores_json:
        lista_professores_json[professor]["nome"] = professor

    return [Document(page_content=str(lista_professores_json[professor])) for professor in lista_professores_json]

def get_response(title, vector_store):    
    llm = ChatOpenAI(model="gpt-4o-mini")

    contextualize_q_system_prompt = f'''
        Você é um assistente de definição de bancas de mestrado.
        Você recebe um título de trabalho de mestrado e deve retornar uma lista de 5 (cinco) nomes de professores que podem ser candidatos a avaliar este mestrado.
        Os professores devem ser escolhidos de acordo com a familiaridade com o os temas tratados no trabalho de mestrado, que devem ser extraídos a partir do título fornecido.  
        Assim, escolha 5 nomes de professores que podem ser candidatos a avaliar o trabalho de mestrado com título {title}
    '''

    theme_extractor_prompt = f'''
        Extraia pelo menos 5 palavras chaves que descrevam este artigo de mestrado de título "{title}".
        Tente responder às perguntas a seguir com base no título fornecido:
        - O trabalho é de qual área do conhecimento? Qual curso de graduação é mais próximo do tema?
        - Quais são os principais objetivos do trabalho? Quais as palavras chave que descrevem o tema geral do trabalho?
        retorne uma lista de 5 (cinco) nomes de professores que podem ser candidatos a avaliar este mestrado. Retorne apenas a lista e mais nenhum texto.
    '''

    with st.status("Definindo bancas", expanded=True):
        st.write("Extraindo temas do título...")
        llm.invoke(theme_extractor_prompt)


        st.write("Procurando professores relevantes...")

        dez_professores_mais_proximos = vector_store.similarity_search_with_score(title, k=10)

        st.write("Checando relevância dos professores encontrados...")
        resposta = llm.invoke(contextualize_q_system_prompt)

    return resposta