# src/search.py
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from prompts.p_search import build_prompt


def _load_env() -> dict:
    """
    Carrega .env e devolve as configs necessárias para busca vetorial.
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

    return {
        "active_provider": active_provider,
        "api_key": api_key,
        "embedding_model": embedding_model,
        "database_url": database_url,
        "collection_name": collection_name,
    }


def _build_embeddings(active_provider: str, api_key: str, embedding_model: str):
    """
    Cria o gerador de embeddings de acordo com o provedor ativo.
    """
    if active_provider == "openai":
        os.environ["OPENAI_API_KEY"] = api_key
        return OpenAIEmbeddings(model=embedding_model)

    if active_provider == "gemini":
        os.environ["GOOGLE_API_KEY"] = api_key
        return GoogleGenerativeAIEmbeddings(model=embedding_model)

    raise ValueError("ACTIVE_PROVIDER inválido. Use 'openai' ou 'gemini'.")


def similarity_search_with_score(query: str, k: int = 10) -> List[Tuple[str, float]]:
    """
    Executa a busca vetorial no PGVector e retorna uma lista de (texto, score).

    Requisito do desafio:
    - buscar os 10 resultados mais relevantes (k=10)
    """
    if not query or not query.strip():
        raise ValueError("Query inválida.")

    cfg = _load_env()
    embeddings = _build_embeddings(cfg["active_provider"], cfg["api_key"], cfg["embedding_model"])

    store = PGVector(
        connection=cfg["database_url"],
        collection_name=cfg["collection_name"],
        embeddings=embeddings,
    )

    results = store.similarity_search_with_score(query.strip(), k=k)
    return [(doc.page_content, float(score)) for doc, score in results]


def search_prompt(question: str) -> str:
    """
    Monta o prompt obrigatório do desafio:
    - vetoriza a pergunta
    - busca k=10 no banco
    - concatena os resultados em CONTEXTO
    - injeta no template
    """
    # k=10 obrigatório pelo enunciado
    results = similarity_search_with_score(question, k=10)

    # for i, (text, score) in enumerate(results, start=1):
    #     print(f"\n--- CHUNK {i} | score={score:.4f} ---\n")
    #     print(text[:300])

    contexto = "\n\n".join(text for text, _score in results)

    return build_prompt(contexto=contexto, pergunta=question)


if __name__ == "__main__":
    q = input("PERGUNTA: ").strip()
    prompt = search_prompt(q)
    print("\n=== PROMPT GERADO (para enviar à LLM) ===\n")
    print(prompt)
