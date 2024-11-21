# Auxiliar para a Definição de Bancas com base em Sistema Lattes

Este projeto é uma aplicação Streamlit que auxilia na definição de bancas de mestrado com base em informações do Sistema Lattes. A aplicação utiliza modelos de linguagem (LLMs) para analisar o título, resumo e palavras-chave do trabalho de mestrado e sugerir professores relevantes para compor a banca.

## Instalação

1. Clone o repositório:
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd banca_chatbot
    ```

2. Crie um ambiente virtual e ative-o:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Execução

Para rodar a aplicação, execute o script `run.bat`:
```bash
.\run.bat
```

## Funcionamento

A aplicação coleta o título, resumo e palavras-chave do trabalho de mestrado e utiliza essas informações para sugerir professores para a banca. O processo é dividido em várias etapas, utilizando diferentes classes e funções:

1. **Carregamento dos Professores**:
    - A função `carrega_professores` no arquivo `base_professores.py` carrega os dados dos professores a partir de um banco de dados vetorial.

2. **Definição da Banca**:
    - A função `define_banca` no arquivo `definidor_banca.py` é responsável por todo o processo de definição da banca. Ela utiliza modelos de linguagem para extrair palavras-chave, gerar variações de título e procurar professores relevantes.

3. **Extração de Palavras-Chave**:
    - A função `extrai_palavraschave_titulo` no arquivo `definidor_banca.py` utiliza um modelo de linguagem para extrair palavras-chave do título e resumo do trabalho de mestrado.

4. **Geração de Variações de Título**:
    - A função `gera_variacoes_titulo` no arquivo `definidor_banca.py` gera variações do título do trabalho de mestrado com base nas palavras-chave extraídas.

5. **Procura de Professores**:
    - A função `procura_professores` no arquivo `definidor_banca.py` procura professores relevantes no banco de dados vetorial utilizando as palavras-chave e variações de título.

6. **Checagem de Relevância**:
    - A função `checa_relevancia` no arquivo `definidor_banca.py` verifica a relevância dos professores encontrados, utilizando um modelo de linguagem para fornecer justificativas detalhadas.

## Configuração do Arquivo .env

Para que a aplicação funcione corretamente, é necessário criar um arquivo `.env` na raiz do projeto para armazenar as API Keys necessárias. Siga os passos abaixo para configurar o arquivo `.env`:

1. Na raiz do projeto, crie um arquivo chamado `.env`.

2. Adicione as seguintes linhas ao arquivo `.env`, substituindo `<SUA_API_KEY>` pelas suas chaves de API correspondentes:
    ```plaintext
    OPENAI_API_KEY=<SUA_API_KEY_OPENAI>
    MISTRAL_API_KEY=<SUA_API_KEY_MISTRAL>
    HF_APIKEY = <SUA_API_KEY_HUGGINGFACE>
    ```

3. Salve o arquivo `.env`.

Essas variáveis de ambiente serão carregadas automaticamente pela aplicação, permitindo o acesso às APIs necessárias para o funcionamento do sistema.

## Estrutura do Projeto

- `main.py`: Arquivo principal que define a interface Streamlit.
- `service`: Diretório que contém os serviços utilizados na aplicação.
    - `definidor_banca.py`: Contém as funções principais para definição da banca.
    - `base_professores.py`: Contém funções para carregar e gerenciar os dados dos professores.
- `models`: Diretório que contém os modelos utilizados na aplicação.
    - `responses_models.py`: Define os modelos de dados utilizados na aplicação.
    - `enums.py`: Define enums utilizados na aplicação.


## Observação

Este trabalho foi realizado para a disciplina de “Aprendizado Profundo” do [Programa de Pós-Graduação em Ciência da Computação (PPGCC) da Unesp](https://www.ibilce.unesp.br/#!/pos-graduacao/programas-de-pos-graduacao/ciencia-da-computacao/apresentacao/), ministrada pelo Prof. Dr. Denis Henrique Pinheiro Salvadeo.