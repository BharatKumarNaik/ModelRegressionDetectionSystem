"""
Assembles the end-to-end agent: retrieve schema context -> generate SQL ->
execute it -> summarize the result in natural language.
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

import sys
from src.config.settings import LLM_MODEL, LLM_TEMPERATURE
from src.database.query_executor import execute_sql_query
from src.llm.prompts import sql_prompt, summary_prompt
from src.llm.vector_store import combine_documents
from src.utils.logger import logging
from src.utils.exception import MRDException
import time
gemini_model = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)


def invoke_with_metrics(prompt_value):
    try:
        start = time.perf_counter()
        response = gemini_model.invoke(prompt_value)
        latency_ms = (time.perf_counter() - start) * 1000
        return {
            "answer": response.content,
            "latency_ms": latency_ms,
            "input_tokens": response.usage_metadata.get("input_tokens"),
            "output_tokens": response.usage_metadata.get("output_tokens"),
            "total_tokens": response.usage_metadata.get("total_tokens"),
            "model": response.response_metadata.get("model_name"),
            "prompt_version": "v1",
        }
    except Exception as e:
        raise MRDException(e,sys) from e

# sql_generation_chain = sql_prompt | gemini_model | StrOutputParser() 
# if we use StrOutputParser() it will directly fetch us the generated output.
# but we need metadata of model execution example: i/p, o/p tokens etc for evaluation.
sql_generation_chain = sql_prompt | RunnableLambda(invoke_with_metrics)
summary_generation_chain = summary_prompt | RunnableLambda(invoke_with_metrics)


def _execute_and_log(data: dict):
    try:
        sql_script = data['sql_script']
        logging.info("Generated SQL:\n%s", sql_script)
        result = execute_sql_query(sql_script)
        logging.info("Query returned %d rows", len(result["rows"]))
        return result
    except Exception as e:
        raise MRDException(e,sys) from e


def build_agent_chain(schema_retriever):
    """
    question -> {question, schema_context} -> {..., sql_result} -> summary
    """
    try:
        return (
        RunnablePassthrough.assign(
            schema_context=(
                lambda x: x["question"]
            )
            | schema_retriever
            | RunnableLambda(combine_documents)
        )
        | RunnablePassthrough.assign(
            sql_llm=sql_generation_chain
        )
        | RunnablePassthrough.assign(
            sql_script=lambda x: x["sql_llm"]["answer"]
        )
        | RunnablePassthrough.assign(
            sql_result=RunnableLambda(_execute_and_log)
        )
        | RunnablePassthrough.assign(
            summary_llm=summary_generation_chain
        )
        | RunnablePassthrough.assign(
            final_answer=lambda x: x["summary_llm"]["answer"]
        )
        )
    except Exception as e:
        raise MRDException(e,sys) from e
