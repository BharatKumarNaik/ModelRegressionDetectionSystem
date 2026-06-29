"""
Assembles the end-to-end agent: retrieve schema context -> generate SQL ->
execute it -> summarize the result in natural language.
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config.settings import LLM_MODEL, LLM_TEMPERATURE
from src.database.query_executor import execute_sql_query
from src.llm.prompts import sql_prompt, summary_prompt
from src.llm.vector_store import combine_documents
from src.utils.logger import logging


gemini_model = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

sql_generation_chain = sql_prompt | gemini_model | StrOutputParser()
summary_generation_chain = summary_prompt | gemini_model | StrOutputParser()


def _execute_and_log(sql_script: str):
    logging.info("Generated SQL:\n%s", sql_script)
    result = execute_sql_query(sql_script)
    logging.info("Query returned %d rows", len(result["rows"]))
    return result


def build_agent_chain(schema_retriever):
    """
    question -> {question, schema_context} -> {..., sql_result} -> summary
    """
    return (
        RunnablePassthrough.assign(
            schema_context=(lambda x: x["question"]) 
                            | schema_retriever 
                            | RunnableLambda(combine_documents)
        )
        | RunnablePassthrough.assign(
            sql_result=sql_generation_chain | RunnableLambda(_execute_and_log)
        )
        | summary_generation_chain
    )
