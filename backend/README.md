# Módulo Backend - Chatbot Inova #
Este módulo é responsável por toda a **lógica de negócio** e pela **exposição de APIs** que sustentam o Chatbot Inova.  
Ele integra os serviços externos (MinIO, Postgres, RabbitMQ e Redis), gerencia a base de conhecimento e fornece os endpoints consumidos pelo agente conversacional.

## Ambiente de Desenvolvimento #
Este projeto utiliza um ambiente virtual (venv), dependências listadas no arquivo `requirements.txt` e variáveis de ambiente configuradas em um arquivo `.env`.  
Também depende de serviços externos em containers Docker: **MinIO**, **Postgres**, **RabbitMQ** e **Redis**.

### Configuração
> _Guia para Configuração do Ambiente de Desenvolvimento_

1. **Criar rede Docker dedicada**:
   ```bash
   docker network create chatbotinova
   ```

2. **Subir containers necessários**:

    Dentro do diretório `stack_chatbotinova` rodar os comandos:

   ```bash
   docker compose -f minio.yml up -d
   docker compose -f postgres.yml up -d
   docker compose -f rabbitmq.yml up -d
   docker compose -f redis.yml up -d
   ```

**Atenção: os próximos passos devem ser feitos dentro da pasta "backend"**

3. **Criar ambiente virtual no VS Code (Windows)**:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configurar arquivo `.env`**:
   Crie um arquivo `.env` baseado no `.env.example` presente no repositório e preencha as chaves de Qdrant, Groq, Postgres e MinIO.

   #### Como obter QDRANT\_URL e QDRANT\_API\_KEY

    1. Acesse [Qdrant Cloud](https://qdrant.tech/documentation/cloud-intro/)
    2. Faça o cadastro e crie um cluster.
    3. Use o endpoint do cluster como `QDRANT_URL` e a chave de API gerada como `QDRANT_API_KEY`.
    
    #### Como obter GROQ\_API\_KEY
    
    1. Acesse [Groq console](https://console.groq.com/home)
    2. Faça o cadastro e crie uma apikey.
    
    #### Como obter credenciais do MinIO
    
    1. Acesse (http://localhost:9001/)
    2. Faça o login com o dados descritos no arquivo minio.yml (MINIO_ROOT_USER, MINIO_ROOT_PASSWORD).
    3. Vá em Access keys e crie uma nova.
    4. MINIO_ENDPOINT=localhost:9002

6. **Inserir documentos na base de conhecimento**:
   Antes de rodar o projeto, é necessário inserir os documentos (PDFs) que ficarão disponíveis para busca pelo RAG.
   O repositório contém um script chamado script_insercao_pdfs.py que faz a leitura dos arquivos da pasta files e insere tudo no banco vetorial e no MinIO.
   
   Atualize o caminho da variável `PDF_FOLDER` no script `script_insercao_pdfs.py` e execute:

   ```powershell
   python -m app.modules.base_de_conhecimento.script_insercao_pdfs
   ```
   Esse processo deve ser feito apenas uma vez, depois os arquivos ficarão salvos e qualquer outra inserção poderá ser feita via a API.

### Execução

> *Guia para Execução do Ambiente de Desenvolvimento*

Para rodar o projeto, execute no terminal:

```powershell
uvicorn app.main:app --reload
```

Isso iniciará o servidor da API do **Chatbot Inova**.
