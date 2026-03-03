"""
Chat CLI — responde perguntas sobre o PDF com busca semântica + LLM.
Ponto de entrada: python src/chat.py
"""
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from search import search

# Alternativa Google (descomente para usar):
# from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

llm = ChatOpenAI(model="gpt-5-nano", temperature=0)
# Alternativa Google (descomente para usar):
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)


def ask(question: str) -> str:
    """Busca chunks relevantes, monta o prompt e retorna a resposta da LLM."""
    results = search(question, k=10)
    contexto = "\n\n---\n\n".join([doc.page_content for doc, score in results])
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pergunta=question)
    response = llm.invoke(prompt)
    return response.content


def main():
    print("=" * 60)
    print("Chat com PDF — Busca Semântica + LangChain + pgVector")
    print("=" * 60)
    print("Digite 'sair' para encerrar.")
    print()
    while True:
        question = input("PERGUNTA: ").strip()
        if question.lower() in ("sair", "exit", "quit"):
            print("Até logo!")
            break
        if not question:
            continue
        response = ask(question)
        print(f"RESPOSTA: {response}")
        print("-" * 60)


if __name__ == "__main__":
    main()
