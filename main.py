from service import definidor_banca, base_professores
from domain.enums import ModelEnum
from statistics import mean
import streamlit as st


st.set_page_config(page_title="Auxiliar para a Definição de Bancas com base em Sistema Lattes")
st.title("Auxiliar para a Definição de Bancas com base em Sistema Lattes")

left, middle, right = st.columns(3)

llm_model = right.selectbox("Escolha o modelo de LLM", [m.value for m in ModelEnum])

vector_store = base_professores.carrega_professores(llm_model)

st.text_input("Qual o título do seu trabalho de mestrado?", key="master_title")
st.text_area ("Cole o resumo do seu mestrado", key="master_summary")
st.text_input("Escolha palavras-chave separadas por ponto vírgula(;) para o seu mestrado", key="master_keywords")


left, middle, right = st.columns(3)
if middle.button("Enviar", use_container_width=True):
    response = definidor_banca.define_banca(
        st.session_state.master_title,
        st.session_state.master_summary,
        st.session_state.master_keywords,
        llm_model,
        vector_store)
    
    response_banca = [p for p in response if p.relevante]
    st.subheader("Possíveis professores para a banca")
    st.header(st.session_state.master_title)
    for professor in response_banca:
        left, middle = st.columns((3, 6))
        left.image(professor.foto, caption=professor.nome)
        middle.subheader(professor.nome)
        middle.write(professor.justificativa_relevancia)
        left.write(f"Relevância: {mean(professor.lista_similaridade) * 100}%")
    
    response_nao_relevante = [p for p in response if not p.relevante]
    st.header("Professores não relevantes")
    for professor in response_nao_relevante:
        middle, right = st.columns((6, 3))
        right.image(professor.foto, caption=professor.nome)
        middle.write(professor.justificativa_relevancia)
        right.write(f"Relevância: {mean(professor.lista_similaridade)*100}%")
