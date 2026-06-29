"""
Entry point for the LLM-driven SQL agent. Wires together:
schema extraction -> document building -> vector store -> agent chain.
"""
from src.database.schema_extractor import get_database_schema, get_table_relationships
from src.llm.chains import build_agent_chain
from src.llm.schema_documents import build_schema_documents
from src.llm.vector_store import build_vector_store, get_schema_retriever
from src.utils.logger import logging



def run_query(question: str) -> str:
    database_schema = get_database_schema()
    relationships = get_table_relationships()

    documents = build_schema_documents(database_schema, relationships)
    vector_db = build_vector_store(documents)
    schema_retriever = get_schema_retriever(vector_db)

    agent_chain = build_agent_chain(schema_retriever)

    logging.info("Invoking agent chain for question: %s", question)
    return agent_chain.invoke({"question": question})


if __name__ == "__main__":
    user_query = "Which customers frequently place large orders but receive partial deliveries?"
    answer = run_query(user_query)
    print("\n--- Final Agent Answer ---")
    print(answer)

# Server=localhost;Database=master;Trusted_Connection=True;
# sqlcmd -S localhost -C