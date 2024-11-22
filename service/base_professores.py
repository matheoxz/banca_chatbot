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
    """
    Carrega os dados dos professores com base no modelo de linguagem especificado.
    Args:
        llm_model (str): O modelo de linguagem a ser utilizado.
    Returns:
        O resultado da função carrega_databasevetorial, que carrega a base de dados vetorial com o diretório e embeddings especificados.
    """
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
    """
    Carrega ou popula um banco de dados vetorial.

    Esta função verifica se o diretório de persistência existe e não está vazio.
    Se o diretório existir e contiver arquivos, carrega o banco de dados vetorial a partir do diretório.
    Caso contrário, popula o banco de dados vetorial.

    Args:
        persist_directory (str): O caminho do diretório onde o banco de dados vetorial é persistido.
        embeddings (function): A função de embeddings utilizada para criar ou carregar o banco de dados vetorial.

    Returns:
        Chroma: Uma instância do banco de dados vetorial carregado ou populado.
    """
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        vectordb = Chroma(collection_name="professores", persist_directory= persist_directory, embedding_function = embeddings)
    else:
        vectordb = popula_databasevetorial(persist_directory, embeddings)
    return vectordb

def popula_databasevetorial(persist_directory, embeddings):
    """
    Popula a base de dados vetorial com documentos de professores.
    Args:
        persist_directory (str): O diretório onde a base de dados vetorial será persistida.
        embeddings (function): A função de embeddings a ser utilizada para a vetorização dos documentos.
    Returns:
        Chroma: A instância da base de dados vetorial preenchida com os documentos dos professores.
    """
    prog_bar = st.progress(0, "Carregando dados de professores...")
    try:
        professores_documentos = carrega_JSON()
        vectordb = Chroma(collection_name="professores", persist_directory= persist_directory, embedding_function = embeddings)
        
        for i, doc in enumerate(professores_documentos):
            print("Adicionando professor: ", i)
            try:
                vectordb.add_documents([doc], id=str(uuid4()))
            except:
                print(f"Erro ao adicionar professor: {Professor.from_Document(doc).nome} \n {e}")
            prog_bar.progress(i/len(professores_documentos))
        prog_bar.progress(1.0).balloons()

    except Exception as e:
        print(e)

    return vectordb
        
def carrega_JSON(caminho_documento = './data/json_curriculos.json'):
    """
    Carrega um arquivo JSON contendo informações de professores e retorna uma lista de objetos Document.
    Args:
        caminho_documento (str): O caminho para o arquivo JSON. O padrão é './data/json_curriculos.json'.
    Returns:
        list: Uma lista de objetos Document, onde cada objeto representa um professor com suas informações.
    """
    with open(caminho_documento, 'r', encoding='utf-8') as file:
        lista_professores_json = json.load(file)
        
    for professor in lista_professores_json:
        lista_professores_json[professor]["nome"] = professor

    return [Document(page_content=str(lista_professores_json[professor])) for professor in lista_professores_json]