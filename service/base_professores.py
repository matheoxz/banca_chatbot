import json
import os
import streamlit as st
from uuid import uuid4
from dotenv import load_dotenv

from langchain.docstore.document import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_chroma import Chroma

from domain.enums import ModelEnum
from domain.responses_models import Professor

def carrega_professores(llm_model: str):
    load_dotenv()
    if llm_model not in [ModelEnum.CHATGPT.value]:
        llm_model = "Vertex"

    persist_directory = f"data/vectorstore/{llm_model}"

    match llm_model:
        case ModelEnum.CHATGPT.value:
            embeddings = OpenAIEmbeddings()
        case "Vertex":
            embeddings = VertexAIEmbeddings(model="text-embedding-004")
        
    return carrega_databasevetorial(persist_directory, embeddings)

def carrega_databasevetorial(persist_directory, embeddings):
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        vectordb = Chroma(collection_name="professores", persist_directory= persist_directory, embedding_function = embeddings)
    else:
        vectordb = popula_databasevetorial(persist_directory, embeddings)
    return vectordb

def popula_databasevetorial(persist_directory, embeddings):
    prog_bar = st.progress(0, "Carregando dados de professores...")
    try:
        professores_documentos = carrega_JSON()
        vectordb = Chroma(collection_name="professores", persist_directory= persist_directory, embedding_function = embeddings)
        
        for i, doc in enumerate(professores_documentos):
            print("Adicionando professor: ", i)
            try:
                vectordb.add_documents([doc], id=str(uuid4()))
            except:
                diminui_dados_professor(vectordb, doc)
            prog_bar.progress(i/len(professores_documentos))
        prog_bar.progress(100)

    except Exception as e:
        print(e)
    return vectordb

def diminui_dados_professor(vectordb, doc):
    professor = Professor.from_Document(doc)
    prof_resumido = '''
                {
                    "nome": "''' + str(professor.nome) + '''",
                    "foto": "''' + str(professor.foto) + '''",
                    "linhas_pesquisa": "''' + str(professor.linhas_pesquisa) + '''"
                }
                '''
    new_doc = Document(page_content=prof_resumido)
    try:
        vectordb.add_documents([new_doc], id=str(uuid4()))
    except Exception as e:
        print(f"Erro ao adicionar professor: {professor.nome} \n {e}")
    
def carrega_JSON(caminho_documento = './data/json_curriculos.json'):
    with open(caminho_documento, 'r', encoding='utf-8') as file:
        lista_professores_json = json.load(file)
        
    for professor in lista_professores_json:
        lista_professores_json[professor]["nome"] = professor

    return [Document(page_content=str(lista_professores_json[professor])) for professor in lista_professores_json]