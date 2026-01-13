# src/ingest.py
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings


# -----------------------------
# Config / leitura do ambiente
# -----------------------------

@dataclass(frozen=True)
class Settings:
    active_provider: str
    api_key: str
    embedding_model: str
    database_url: str
    collection_name: str
    pdf_path: Path


def load_settings() -> Settings:
    """
    Carrega configurações do .env e valida os campos obrigatórios.
    """
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    active_provider = os.getenv("ACTIVE_PROVIDER", "openai").strip().lower()
    database_url = os.getenv("DATABASE_URL", "")
    collection_name = os.getenv("PG_VECTOR_COLLECTION_NAME", "documents")

    if not database_url:
        raise RuntimeError("DATABASE_URL não foi definido no arquivo .env")

    if active_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY não foi definido no arquivo .env")
        if not embedding_model:
            raise RuntimeError("OPENAI_EMBEDDING_MODEL não foi definido no arquivo .env")

    elif active_provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY", "")
        embedding_model = os.getenv("GOOGLE_EMBEDDING_MODEL", "")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY não foi definido no arquivo .env")
        if not embedding_model:
            raise RuntimeError("GOOGLE_EMBEDDING_MODEL não foi definido no arquivo .env")

    else:
        raise RuntimeError("ACTIVE_PROVIDER inválido. Use 'openai' ou 'gemini'.")

    pdf_path = resolve_pdf_path(project_root)

    return Settings(
        active_provider=active_provider,
        api_key=api_key,
        embedding_model=embedding_model,
        database_url=database_url,
        collection_name=collection_name,
        pdf_path=pdf_path,
    )


def resolve_pdf_path(project_root: Path) -> Path:
    """
    Resolve o PDF via variável de ambiente PDF_PATH (fallback para document.pdf).
    """
    pdf_path_env = os.getenv("PDF_PATH", "document.pdf")
    pdf_path = Path(pdf_path_env)

    # Se for caminho relativo, resolve a partir da raiz do projeto
    if not pdf_path.is_absolute():
        pdf_path = project_root / pdf_path

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF não encontrado em: {pdf_path}")

    return pdf_path


# -----------------------------
# Embeddings / Provider
# -----------------------------

def build_embeddings(active_provider: str, api_key: str, embedding_model: str):
    """
    Cria o gerador de embeddings conforme o provedor (OpenAI ou Gemini).
    """
    provider = (active_provider or "").strip().lower()

    if provider == "openai":
        # LangChain OpenAI usa OPENAI_API_KEY como padrão.
        os.environ["OPENAI_API_KEY"] = api_key
        return OpenAIEmbeddings(model=embedding_model)

    if provider == "gemini":
        # LangChain Google GenAI usa GOOGLE_API_KEY como padrão.
        os.environ["GOOGLE_API_KEY"] = api_key
        return GoogleGenerativeAIEmbeddings(model=embedding_model)

    raise ValueError("ACTIVE_PROVIDER inválido. Use 'openai' ou 'gemini'.")


# -----------------------------
# Pipeline: load -> split -> store
# -----------------------------

def load_pdf_documents(pdf_path: Path):
    """
    Lê o PDF e retorna documentos (por página) em formato LangChain.
    """
    loader = PyPDFLoader(str(pdf_path))
    return loader.load()


def split_into_chunks(documents):
    """
    Divide o conteúdo em chunks.

    REGRA DO ENUNCIADO (implementada aqui):
    - chunks de 1000 caracteres
    - overlap de 150 caracteres
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,     # regra: 1000 caracteres
        chunk_overlap=150,   # regra: overlap 150
    )
    return splitter.split_documents(documents)


def store_chunks_in_pgvector(chunks, settings: Settings):
    """
    Gera embeddings e armazena no Postgres/pgvector.

    REGRAS DO ENUNCIADO (implementadas aqui):
    - cada chunk é convertido em embedding (PGVector chama o embedding internamente)
    - vetores são armazenados no PostgreSQL com pgvector
    """
    embeddings = build_embeddings(
        active_provider=settings.active_provider,
        api_key=settings.api_key,
        embedding_model=settings.embedding_model,
    )

    # regra: persistir vetores no PostgreSQL + pgvector
    # regra: cada chunk vira embedding e é salvo
    PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        connection=settings.database_url,
        collection_name=settings.collection_name,
    )


# -----------------------------
# Orquestração / entrypoint
# -----------------------------

def ingest_pdf() -> None:
    settings = load_settings()

    print("== Ingestão do PDF ==")
    print(f"PDF: {settings.pdf_path}")
    print(f"Provider: {settings.active_provider}")
    print(f"Embedding model: {settings.embedding_model}")
    print(f"Collection: {settings.collection_name}")
    print(f"Database: {settings.database_url}")

    docs = load_pdf_documents(settings.pdf_path)
    chunks = split_into_chunks(docs)

    if not chunks:
        raise RuntimeError("Nenhum chunk gerado. O PDF pode estar sem texto extraível.")

    print(f"Pages loaded: {len(docs)}")
    print(f"Chunks gerados: {len(chunks)}")

    store_chunks_in_pgvector(chunks, settings)

    print("*** Ingestão finalizada com sucesso! Vetores armazenados no Postgres/pgvector. ***")


if __name__ == "__main__":
    ingest_pdf()
