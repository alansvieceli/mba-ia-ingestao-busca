# Ingestão e Busca Semântica com LangChain e PostgreSQL (pgvector)

Este projeto implementa um **sistema de busca semântica baseado em PDF**, utilizando **LangChain**, **PostgreSQL com pgvector** e **LLMs (OpenAI ou Gemini)**.

O sistema permite:

* Ingerir um arquivo PDF
* Armazenar embeddings vetoriais no banco de dados
* Realizar perguntas via CLI
* Obter respostas **exclusivamente com base no conteúdo do PDF**
* Evitar qualquer tipo de alucinação ou conhecimento externo

---

## 📌 Funcionalidades

### Ingestão

* Leitura de um arquivo PDF local
* Divisão do texto em *chunks* de 1000 caracteres com overlap de 150
* Geração de embeddings
* Persistência dos vetores no PostgreSQL (pgvector)

### Busca e Resposta

* Interface de linha de comando (CLI)
* Vetorização da pergunta do usuário
* Busca dos 10 trechos mais relevantes no banco vetorial
* Geração de resposta via LLM **somente com base no contexto recuperado**
* Perguntas fora do contexto retornam uma resposta padrão

---

## 🧠 Tecnologias utilizadas

* **Python 3.12+**
* **LangChain**
* **PostgreSQL + pgvector**
* **Docker & Docker Compose**
* **OpenAI ou Google Gemini**

---

## 📂 Estrutura do projeto

```
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── src/
│   ├── ingest.py      # Ingestão do PDF
│   ├── search.py      # Busca semântica
│   ├── chat.py        # CLI interativo
├── document.pdf       # PDF para ingestão
└── README.md
```

---

## ⚙️ Pré-requisitos

* Python 3.12 ou superior
* Docker e Docker Compose
* Conta na OpenAI **ou** Google Gemini (para gerar API Key)

---

## 🐍 Ambiente Python

Crie e ative um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## 🐘 Banco de dados (PostgreSQL + pgvector)

Suba o banco via Docker:

```bash
docker compose up -d
```

Verifique se está rodando:

```bash
docker compose ps
```

---

## 🔐 Configuração do `.env`

Crie o arquivo `.env` a partir do template:

```bash
cp .env.example .env
```

Exemplo de configuração:

```env
# === Qual provedor está ativo agora ===
ACTIVE_PROVIDER=openai
# valores possíveis: openai | gemini

# === OpenAI ou Gemini ===
API_KEY=COLE_SUA_CHAVE_AQUI
EMBEDDING_MODEL=text-embedding-3-small

# === Postgres (Docker rodando na sua máquina) ===
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/postgres

# === Nome da coleção/tabela vetorial no pgvector ===
PG_VECTOR_COLLECTION_NAME=documents
```

### 🔄 Trocar entre OpenAI e Gemini

Para usar Gemini, basta alterar:

```env
ACTIVE_PROVIDER=gemini
API_KEY=COLE_SUA_CHAVE_DO_GEMINI
EMBEDDING_MODEL=models/embedding-001
```

Nenhuma alteração de código é necessária.

---

## 📥 Ingestão do PDF

Execute o script de ingestão:

```bash
python src/ingest.py
```

Esse passo:

* Lê o `document.pdf`
* Gera embeddings
* Armazena os vetores no banco

---

## 💬 Chat via CLI

Inicie o chat interativo:

```bash
python src/chat.py
```

Exemplo:

```
Faça sua pergunta:
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.
```

### Perguntas fora do contexto

```
PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

---

## 📏 Regras de resposta

A LLM é instruída a:

* Responder **somente** com base no contexto recuperado
* Não usar conhecimento externo
* Não gerar opiniões
* Retornar uma mensagem padrão caso a resposta não esteja no PDF

---

## 🚨 Observações importantes

* O arquivo `.env` **não deve ser commitado**
* O custo de uso das APIs é baixo para PDFs pequenos
* PDFs escaneados (imagem) podem não gerar texto utilizável

---

## ✅ Status do projeto

* [x] Estrutura definida
* [x] Banco com pgvector via Docker
* [x] Suporte a OpenAI e Gemini
* [ ] Implementação da ingestão
* [ ] Implementação da busca
* [ ] Implementação do chat CLI
