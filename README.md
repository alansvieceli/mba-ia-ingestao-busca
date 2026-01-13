# Ingestão e Busca Semântica com LangChain e PostgreSQL (pgvector)

Este projeto implementa um **sistema completo de busca semântica baseado em PDF**, utilizando **LangChain**, **PostgreSQL com pgvector** e **LLMs (OpenAI ou Gemini)**.

O sistema permite:

* Ingerir um arquivo PDF
* Armazenar embeddings vetoriais no banco de dados
* Realizar perguntas via CLI
* Obter respostas **exclusivamente com base no conteúdo do PDF**
* Evitar qualquer tipo de alucinação ou uso de conhecimento externo

---

## 📌 Funcionalidades

### Ingestão

* Leitura de um arquivo PDF local
* Divisão do texto em *chunks* de **1000 caracteres com overlap de 150**
* Geração de embeddings
* Persistência dos vetores no PostgreSQL (pgvector)

### Busca e Resposta

* Interface de linha de comando (CLI)
* Vetorização da pergunta do usuário
* Busca dos **10 trechos mais relevantes (k=10)** no banco vetorial
* Montagem de prompt restritivo com base **exclusiva** no contexto recuperado
* Geração de resposta via LLM
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
│   ├── ingest.py          # Ingestão do PDF
│   ├── search.py          # Busca semântica + montagem do prompt
│   ├── chat.py            # CLI interativo (end-to-end)
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── p_search.py    # Template de prompt obrigatório
├── document.pdf           # PDF para ingestão (padrão)
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

### Exemplo de configuração (OpenAI)

```env
# === Provedor ativo ===
ACTIVE_PROVIDER=openai
# valores possíveis: openai | gemini

# === OpenAI ===
OPENAI_API_KEY=COLE_SUA_CHAVE_AQUI
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# === Gemini (opcional) ===
GOOGLE_API_KEY=
GOOGLE_EMBEDDING_MODEL=models/embedding-001

# === Postgres (Docker rodando localmente) ===
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/postgres

# === Nome da coleção/tabela vetorial ===
PG_VECTOR_COLLECTION_NAME=documents

# === Caminho do PDF a ser ingerido ===
PDF_PATH=document.pdf
```

---

### 🔄 Alternar entre OpenAI e Gemini

O projeto suporta **apenas um provedor ativo por vez**, controlado pela variável `ACTIVE_PROVIDER`.

#### Usando OpenAI

```env
ACTIVE_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

#### Usando Gemini

```env
ACTIVE_PROVIDER=gemini
GOOGLE_API_KEY=...
GOOGLE_EMBEDDING_MODEL=models/embedding-001
```

> ⚠️ Não é necessário alterar o código para trocar o provedor — apenas o `.env`.

---

### 📄 Configuração do PDF

O caminho do PDF é definido pela variável:

```env
PDF_PATH=document.pdf
```

* Pode ser um caminho relativo (resolvido a partir da raiz do projeto)
* Ou um caminho absoluto:

  ```env
  PDF_PATH=/caminho/completo/para/arquivo.pdf
  ```

---

## 📥 Ingestão do PDF

Execute o script de ingestão:

```bash
python src/ingest.py
```

Esse passo:

* Lê o PDF configurado em `PDF_PATH`
* Divide o conteúdo em **chunks de 1000 caracteres com overlap de 150**
* Gera embeddings para cada chunk
* Armazena os vetores no banco PostgreSQL (pgvector)

---

## 🔎 Busca semântica (sem LLM)

> ⚠️ **Aviso**
> Este passo **não é obrigatório** para o uso do sistema.
> A busca semântica e a montagem do prompt **já são executadas automaticamente pelo `chat.py`** no fluxo completo.
>
> Este script existe **apenas para inspeção, depuração e validação do prompt**, permitindo visualizar exatamente o contexto que será enviado à LLM, **sem realizar chamadas à API**.

Para testar apenas a busca e a montagem do prompt (sem chamar a LLM):

```bash
python src/search.py
```

Esse comando:

* solicita uma pergunta no terminal
* busca os **10 trechos mais relevantes** no banco vetorial
* imprime o **prompt completo** que será enviado à LLM

Esse passo é útil para:

* validar o `CONTEXTO`
* validar o template exigido pelo desafio
* evitar custos desnecessários com LLM

---

## 💬 Chat via CLI (fluxo completo)

Inicie o chat interativo:

```bash
python src/chat.py
```

Exemplo:

```text
Faça sua pergunta:
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.
```

### Perguntas fora do contexto

```text
PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

---

## 📏 Regras de resposta

A LLM é instruída a:

* Responder **somente** com base no contexto recuperado
* Não usar conhecimento externo
* Não gerar opiniões
* Retornar uma mensagem padrão caso a resposta não esteja explicitamente no PDF

---

## 🚨 Observações importantes

* O arquivo `.env` **não deve ser commitado**
* Nunca compartilhe suas API Keys
* O custo de uso das APIs é baixo para PDFs pequenos
* PDFs escaneados (imagem) podem não conter texto extraível

---

## ✅ Status do projeto

* [x] Estrutura definida
* [x] Banco com pgvector via Docker
* [x] Suporte a OpenAI e Gemini via `ACTIVE_PROVIDER`
* [x] Implementação da ingestão
* [x] Implementação da busca semântica
* [x] Implementação do chat CLI (end-to-end)

---

## 📌 Conclusão

Este projeto implementa um fluxo completo de **RAG (Retrieval-Augmented Generation)** de forma explícita e auditável, atendendo rigorosamente aos requisitos do desafio:

* ingestão controlada
* armazenamento vetorial
* busca top-k
* prompt restritivo
* ausência total de alucinações
