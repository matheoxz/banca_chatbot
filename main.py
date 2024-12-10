"""
Este script configura uma aplicação web Streamlit para auxiliar na definição de bancas com base no sistema Lattes.
"""
from service import definidor_banca, base_professores
from domain.enums import ModelEnum
from statistics import mean
import streamlit as st

# Define o título da página e configurações iniciais do Streamlit
page_title = "Auxiliar para a Definição de Bancas com base em Sistema Lattes"
st.set_page_config(page_title=page_title)
st.title(page_title)

# Cria uma seleção na barra lateral para escolher o modelo de LLM
llm_model = st.sidebar.selectbox("Escolha o modelo de LLM", [m.value for m in ModelEnum])

# Carrega os professores com base no modelo selecionado
vector_store = base_professores.carrega_professores(llm_model)

# Cria campos de entrada para o título do trabalho, resumo e palavras-chave
st.text_input("Qual o título do seu trabalho de mestrado?", key="master_title")
st.text_area("Cole o resumo do seu mestrado", key="master_summary")
st.text_input("Escolha palavras-chave separadas por ponto vírgula(;) para o seu mestrado", key="master_keywords")

# Cria três colunas para organizar o layout
left, middle, right = st.columns(3)

# Define a ação do botão "Enviar"
if middle.button("Enviar", use_container_width=True):
    # Chama a função para definir a banca com os dados fornecidos
    response = definidor_banca.define_banca(
        st.session_state.master_title,
        st.session_state.master_summary,
        st.session_state.master_keywords,
        llm_model,
        vector_store)
    
    #ordenando a lista de professores por pontuação
    response.sort(key=lambda p: p.pontuacao, reverse=True)
    st.subheader("Possíveis professores para a banca")
    st.header(st.session_state.master_title)
    
    # Exibe os professores que podem compor a banca
    for professor in response:
        left, middle = st.container(border=True).columns((3, 6))
        left.image(professor.foto, caption=professor.nome)
        middle.subheader(professor.nome)
        middle.write(professor.justificativa_relevancia)
        middle.metric(f"Relevância: ", round(mean(professor.lista_similaridade) * 100, 2))
