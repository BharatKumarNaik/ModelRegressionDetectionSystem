"""
Entry point for the LLM-driven SQL agent. Wires together:
schema extraction -> document building -> vector store -> agent chain.
"""

from src.llm.chains import build_agent_chain
from src.utils.logger import logging
from src.llm.IndexManager import get_vectordb_retriever



def run_query(question: str) -> str:
    schema_retriever = get_vectordb_retriever()
    agent_chain = build_agent_chain(schema_retriever)

    logging.info("Invoking agent chain for question: %s", question)
    return agent_chain.invoke({"question": question})


if __name__ == "__main__":
    user_query = input("Enter your query:")
    answer = run_query(user_query)
    print("\n--- Final Agent Answer ---")
    print(answer['final_answer'])