"""
Entry point for the LLM-driven SQL agent. Wires together:
schema extraction -> document building -> vector store -> agent chain.
"""

from src.llm.chains import build_agent_chain
from src.utils.logger import logging
from src.llm.IndexManager import get_vectordb_retriever
from src.utils.exception import MRDException
from src.evaluation.evaluation import Runner
from src.runner.test_runner import testing_test_runner
import sys

def run_query(question: str) -> str:
    try:
        schema_retriever = get_vectordb_retriever()
        agent_chain = build_agent_chain(schema_retriever)

        logging.info("Invoking agent chain for question: %s", question)
        return agent_chain.invoke({"question": question})
    except Exception as e:
        raise MRDException(e,sys) from e

if __name__ == "__main__":
    user_query = input("Enter your query:")
    answer = run_query(user_query)
    print("\n--- Final Agent Answer ---")
    print(answer['final_answer'])
    testing_test_runner()
    print("Test Runner executed successfully")
    print(Runner.evaluationRunner())
    print("Evaluation and Regression runner executed successfully")

    