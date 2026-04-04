import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.search import search_prompt, _get_vectorstore


def _get_llm():
    if os.getenv("GOOGLE_API_KEY"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)


def main():
    try:
        _get_vectorstore()
    except Exception as e:
        print(f"Não foi possível iniciar o chat. Verifique os erros de inicialização: {e}")
        return

    llm = _get_llm()
    print("Chat RAG iniciado. Digite 'sair' para encerrar.")

    while True:
        query = input("\nPergunta: ").strip()
        if query.lower() in ["sair", "exit", "quit"]:
            break
        if not query:
            continue

        try:
            prompt_text = search_prompt(query)
            response = llm.invoke(prompt_text)
            print(f"\nResposta: {response.content}")
        except Exception as e:
            print(f"\n[Erro] {e}")

    print("Chat encerrado.")


if __name__ == "__main__":
    main()
