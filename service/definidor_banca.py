import streamlit as st
from langchain_chroma import Chroma
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI

from domain.enums import ModelEnum
from domain.responses_models import ListaPalavrasChave, ListaVariacoesTitulo, ListaProfessores, Professor, ListaRelevanciaProfessores

def define_banca(titulo: str, resumo: str, palavras_chave: str, modelo: ModelEnum, vector_store: Chroma): 
    """
    Define a banca examinadora com base no título, resumo e palavras-chave fornecidos.
    Args:
        titulo (str): O título do trabalho.
        resumo (str): O resumo do trabalho.
        palavras_chave (str): Palavras-chave separadas por ponto e vírgula.
        modelo (ModelEnum): Enum que define o modelo de linguagem a ser utilizado.
        vector_store (Chroma): Base de dados vetorial para busca de professores.
    Returns:
        lista_professores_final (list): Lista de professores sugeridos para a banca, ordenados por relevância.
    """
    # Seleciona o modelo de linguagem com base no enum fornecido
    match modelo:
        case ModelEnum.CHATGPT.value:
            llm = ChatOpenAI(model="gpt-4o-mini")
        case ModelEnum.GEMINI.value:
            llm = ChatVertexAI(model="gemini-1.5-flash-001")

    # Exibe status no Streamlit
    with st.status("Definindo banca", expanded=True):
        # Extrai palavras-chave do título e resumo
        palavras_chave_extraidas_titulo = extrai_palavraschave_titulo(titulo, resumo, llm)
        set_palavraschave = set(palavras_chave_extraidas_titulo.palavras_chave).union(set(palavras_chave.split(";")))

        # Gera variações do título
        variacoes_titulo = gera_variacoes_titulo(titulo, resumo, set_palavraschave, llm)
        variacoes_titulo.titulos.extend([titulo, resumo])

        # Procura professores relevantes
        lista_professores = procura_professores(vector_store, set_palavraschave, variacoes_titulo).ordena_por_relevancia()
        
        # Checa a relevância dos professores encontrados
        lista_professores_final = checa_relevancia(resumo, llm, set_palavraschave, variacoes_titulo, lista_professores)

        st.write("Sugestão de Banca definida!")
    
    return lista_professores_final

def extrai_palavraschave_titulo(titulo: str, resumo:str, llm: BaseChatModel) ->  ListaPalavrasChave:
    """
    Extrai palavras-chave do título e resumo de um trabalho de mestrado.
    Args:
        titulo (str): O título do trabalho de mestrado.
        resumo (str): O resumo do trabalho de mestrado.
        llm (BaseChatModel): Modelo de linguagem utilizado para a extração das palavras-chave.
    Returns:
        ListaPalavrasChave: Objeto contendo as palavras-chave extraídas do título e resumo.
    """
    theme_extractor_prompt = f'''
        A partir do título "{titulo}" e do resumo abaixo, extraia as áreas de pesquisa do trabalho de mestrado.
        Resumo: {resumo}
        Tente responder às perguntas a seguir com base no título e resumo fornecidos:
            - O trabalho é de qual área do conhecimento? Qual curso de graduação é mais próximo do tema?
            - Quais são os principais objetivos do trabalho? Quais as palavras chave que descrevem o tema geral do trabalho?
            - O que o trabalho se propõe a pesquisar? Qual pergunta ele tenta responder?
    '''
    st.write("Extraindo áreas de pesquisa do título...")
    
    #Chamada ao LLM para extrair as áreas de pesquisa
    structured_llm = llm.with_structured_output(ListaPalavrasChave)
    resposta = structured_llm.invoke(theme_extractor_prompt)

    st.write(f"Palavras-chave a partir do título e resumo")
    st.write(resposta.palavras_chave)

    return resposta

def gera_variacoes_titulo(titulo: str, resumo:str, palavraschave: set, llm: BaseChatModel) -> ListaVariacoesTitulo:
    """
    Gera variações de título para um trabalho de mestrado com base no título original, resumo e palavras-chave fornecidos.
    Args:
        titulo (str): O título original do trabalho de mestrado.
        resumo (str): O resumo do trabalho de mestrado.
        palavraschave (set): Um conjunto de palavras-chave relacionadas ao trabalho.
        llm (BaseChatModel): Um modelo de linguagem que será usado para gerar as variações de título.
    Returns:
        ListaVariacoesTitulo: Uma lista contendo as variações de título geradas.
    """
    theme_extractor_prompt = f'''
        Sugira 5 novos títulos para o trabalho de mestrado com título {titulo} e palavras chave {palavraschave}.
        Resumo: {resumo}
        Tente destacar algumas palavras-chaves no título e use-as como base para gerar novas variações, combinando-as de deiversas formas.
    '''
    st.write("Variando título...")

    #Chamada ao LLM para gerar as variações de título
    structured_llm = llm.with_structured_output(ListaVariacoesTitulo)
    resposta = structured_llm.invoke(theme_extractor_prompt)

    st.write(f"Titulos para mestrado: ")
    st.write(resposta.titulos)

    return resposta

def procura_professores(vector_store: Chroma, set_palavraschave: set, variacoes_titulo: ListaVariacoesTitulo) -> ListaProfessores:
    """
    Procura professores relevantes com base em um conjunto de palavras-chave e variações de títulos.

    Args:
        vector_store (Chroma): Objeto que permite realizar buscas de similaridade.
        set_palavraschave (set): Conjunto de palavras-chave para a busca.
        variacoes_titulo (ListaVariacoesTitulo): Objeto contendo variações de títulos para a busca.

    Returns:
        ListaProfessores: Lista de professores encontrados com base na busca de similaridade.
    """
    st.write("Procurando professores relevantes...")

    # Busca os professores mais próximos para cada variação de título
    lista_professores = ListaProfessores(professores=[])
    for titulo in variacoes_titulo.titulos:
        cinco_professores_mais_proximos = vector_store.similarity_search_with_relevance_scores(f"{titulo} {set_palavraschave}", k=5)
        lista_professores.add_professores([Professor.from_tuple_json_similarity(professor) for professor in cinco_professores_mais_proximos])
    
    st.write(f"{len(lista_professores.professores)} Professores encontrados!")

    return lista_professores

# Função para checar a relevância dos professores encontrados
def checa_relevancia(resumo, llm, set_palavraschave, variacoes_titulo, lista_professores: ListaProfessores) -> list[Professor]:
    """
    Verifica a relevância dos professores para um trabalho de mestrado com base no resumo, palavras-chave e variações de título fornecidos.
    Args:
        resumo (str): Resumo do trabalho de mestrado.
        llm (LLM): Modelo de linguagem utilizado para análise.
        set_palavraschave (set): Conjunto de palavras-chave que descrevem a área de pesquisa e objetivos.
        variacoes_titulo (VariacoesTitulo): Objeto contendo variações de títulos do trabalho de mestrado.
        lista_professores (ListaProfessores): Lista de professores candidatos a avaliar o trabalho de mestrado.
    Returns:
        list[Professor]: Lista de professores com a relevância atualizada e justificativas.
    """
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
    st.write("Checando relevância dos professores encontrados...")

    # Estrutura o LLM para responder a relevância dos professores
    structured_llm = llm.with_structured_output(ListaRelevanciaProfessores)
    lista_relevancia = ListaRelevanciaProfessores()
    lista_professores_ = lista_professores.professores

    # Chamadas ao LLM para definir a relevância de cada professor
    for id in range(0, len(lista_professores_), 5): # Chama o LLM de 5 em 5 professores
        resposta = define_relevancia(structured_llm, contextualize_q_system_prompt, lista_professores_, id)
        lista_relevancia.add_relevancias(resposta.relevancia_professores)
    
    # Atualiza a relevância dos professores na lista
    inclui_relevancia_professor(lista_relevancia, lista_professores_)

    st.write(f"{sum(1 for p in lista_professores_ if p.relevante)} professores relevantes encontrados!")

    return lista_professores_

def define_relevancia(structured_llm, prompt: str, lista_professores: list[Professor], id: int) -> ListaRelevanciaProfessores:
    """
    Define a relevância de professores com base em um prompt fornecido.

    Args:
        structured_llm: Um modelo de linguagem estruturado com ListaRelevanciaProfessores como saída.
        prompt (str): O prompt que será usado para gerar a resposta.
        lista_professores (list[Professor]): Uma lista de objetos Professor que serão usados para gerar a resposta.
        id (int): O índice inicial na lista de professores para selecionar um subconjunto de professores enviàdos ao modelo.

    Returns:
        resposta (ListaRelevanciaProfessores): A resposta gerada pelo modelo de linguagem estruturado com base no prompt e nos professores selecionados.
    """
    # Define a função lambda para calcular o índice final, garantindo que não exceda o tamanho da lista
    id_final = lambda x: x+5 if x+5 < len(lista_professores) else len(lista_professores)
    
    # Seleciona um subconjunto de cinco professores a partir do índice atual
    cinco_professores = lista_professores[id: id_final(id)]
    
    # Converte a lista de cinco professores em uma string formatada para o prompt
    cinco_professores_str = "\n".join([("{" + f'"nome":"{professor.nome}", "resumo": "{professor.resumo}", "linhas_pesquisa": "{professor.linhas_pesquisa}"' + "}") for professor in cinco_professores])
    
    # Invoca o modelo de linguagem estruturado com o prompt e a string dos cinco professores
    resposta = structured_llm.invoke(prompt + f"\nProfessores: {cinco_professores_str}")
    
    # Retorna a resposta gerada pelo modelo de linguagem
    return resposta

def inclui_relevancia_professor(lista_relevancia:ListaRelevanciaProfessores, professores: list[Professor]):
    """
    Atualiza a relevância dos professores na lista de professores fornecida com base na lista de relevância.

    Para cada professor na lista de professores, verifica se ele está presente na lista de relevância.
    Se estiver presente, atualiza os atributos 'relevante' e 'justificativa_relevancia' do professor.
    Se não estiver presente, imprime uma mensagem informando que o professor não foi encontrado na lista de relevância.

    Args:
        lista_relevancia (ListaRelevanciaProfessores): A lista contendo a relevância dos professores.
        professores (list[Professor]): A lista de professores a serem atualizados.
    """
    for professor in professores:
        professor_na_lista = next((p for p in lista_relevancia.relevancia_professores if p.nome == professor.nome), None)
        if professor_na_lista is not None:
            professor.relevante = professor_na_lista.relevante
            professor.justificativa_relevancia = professor_na_lista.justificativa
        else:
            print(f"Professor {professor.nome} não encontrado na lista de relevância")