# src/chat.py
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from search import search_prompt


def load_llm():
    """
    Inicializa a LLM de acordo com o ACTIVE_PROVIDER.
    """
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    active_provider = os.getenv("ACTIVE_PROVIDER", "openai").strip().lower()

    if active_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY não definido no .env")
        os.environ["OPENAI_API_KEY"] = api_key

        model = os.getenv("OPENAI_LLM_MODEL", "gpt-5-nano")
        return ChatOpenAI(model=model, temperature=0)

    if active_provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY não definido no .env")
        os.environ["GOOGLE_API_KEY"] = api_key

        model = os.getenv("GOOGLE_LLM_MODEL", "gemini-2.5-flash-lite")
        return ChatGoogleGenerativeAI(model=model, temperature=0)

    raise RuntimeError("ACTIVE_PROVIDER inválido. Use 'openai' ou 'gemini'.")


def main() -> None:
    llm = load_llm()

    print("Faça sua pergunta (digite 'sair' para encerrar):\n")

    while True:
        question = input("PERGUNTA: ").strip()

        if not question:
            print("Digite uma pergunta válida.\n")
            continue

        if question.lower() in {"sair", "exit", "quit"}:
            print("Encerrando.")
            break

        # 🔹 chama a busca + prompt
        prompt = search_prompt(question)

        # 🔹 envia o prompt para a LLM
        response = llm.invoke(prompt)

        # LangChain retorna objeto de mensagem
        answer = getattr(response, "content", str(response)).strip()

        print(f"RESPOSTA: {answer}\n")


if __name__ == "__main__":
    main()

