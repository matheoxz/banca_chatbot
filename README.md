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
    - Os dados de professores foram extraídos da plataforma Lattes num arquivo JSON através do código do repositório [Lattes-Downloader](https://github.com/joaotinti75/Lattes-Downloader).

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

## Configuração do Arquivo .env para ChatGPT

Para que a aplicação funcione corretamente, é necessário criar um arquivo `.env` na raiz do projeto para armazenar as API Keys necessárias. Siga os passos abaixo para configurar o arquivo `.env`:

1. Na raiz do projeto, crie um arquivo chamado `.env`.

2. Adicione as seguintes linhas ao arquivo `.env`, substituindo `<SUA_API_KEY>` pelas suas chaves de API correspondentes:
    ```plaintext
    OPENAI_API_KEY=<SUA_API_KEY_OPENAI>
    ```

3. Salve o arquivo `.env`.

Essas variáveis de ambiente serão carregadas automaticamente pela aplicação, permitindo o acesso às APIs necessárias para o funcionamento do sistema.

### Configuração do Arquivo .env para Gemini

Para utilizar os modelos GEMINI, é necessário configurar a variável de ambiente `GOOGLE_APPLICATION_CREDENTIALS`. Siga os passos abaixo para gerar e configurar suas credenciais no Google Cloud com Vertex AI:

1. **Criação do Projeto no Google Cloud**:
    - Acesse o [Google Cloud Console](https://console.cloud.google.com/).
    - Crie um novo projeto ou selecione um projeto existente.

2. **Ativação da API Vertex AI**:
    - No painel de navegação, vá para "APIs e serviços" > "Biblioteca".
    - Pesquise por "Vertex AI" e ative a API.

3. **Criação da Conta de Serviço**:
    - Vá para "IAM e administrador" > "Contas de serviço".
    - Clique em "Criar conta de serviço".
    - Preencha os detalhes da conta de serviço e clique em "Criar e continuar".
    - Conceda à conta de serviço o papel "Administrador do Vertex AI" e clique em "Concluído".

4. **Geração da Chave JSON**:
    - Na lista de contas de serviço, encontre a conta de serviço criada.
    - Clique nos três pontos ao lado da conta de serviço e selecione "Gerenciar chaves".
    - Clique em "Adicionar chave" > "Criar nova chave".
    - Selecione o formato JSON e clique em "Criar". O arquivo JSON será baixado para o seu computador.

5. **Configuração da Variável de Ambiente**:
    - Mova o arquivo JSON para o diretório raiz do seu projeto.
    - Adicione a seguinte linha ao seu arquivo `.env`, substituindo `<CAMINHO_PARA_O_ARQUIVO_JSON>` pelo caminho para o arquivo JSON:
    ```plaintext
    GOOGLE_APPLICATION_CREDENTIALS=<CAMINHO_PARA_O_ARQUIVO_JSON>
    ```

6. **Salve o arquivo `.env`**.

Com essas configurações, a aplicação poderá acessar os modelos GEMINI utilizando as credenciais do Google Cloud.


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