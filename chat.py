from llm_chains import carrega_profs
import streamlit as st


st.set_page_config(page_title="Auxiliar para a Definição de Bancas com base em Sistema Lattes")
st.title("Auxiliar para a Definição de Bancas com base em Sistema Lattes")

vector_store = carrega_profs.carregaProfessores()

st.text_input("Qual o título do seu trabalho de mestrado?", key="master_title")

if st.button("Enviar"):
    response = carrega_profs.get_response(st.session_state.master_title, vector_store)
    st.write(response)