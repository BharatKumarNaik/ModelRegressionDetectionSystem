'''
load golden dataset -> call model for each question -> collect and save the result
'''
'''
{
id: "TC_001",
question:"",
sql_script:"",
sql_result:"",
sql_llm:{
    'latency_ms': 2328.8173999999344, 
    'input_tokens': 1431, 
    'output_tokens': 148, 
    'total_tokens': 1579, 
    'model': 'gemini-2.5-flash', 
    'prompt_version': 'v1'
    },
final_answer:"",
summary_llm:{
    'latency_ms': 2328.8173999999344, 
    'input_tokens': 1431, 
    'output_tokens': 148, 
    'total_tokens': 1579, 
    'model': 'gemini-2.5-flash', 
    'prompt_version': 'v1'
    }
}
'''

"""
Entry point for the LLM-driven SQL agent. Wires together:
schema extraction -> document building -> vector store -> agent chain.
"""

from src.llm.chains import build_agent_chain
from src.utils.logger import logging
from src.llm.IndexManager import get_vectordb_retriever
from src.config.settings import TEST_ARTIFACTS_DIR,GOLDEN_DATASET_PATH
from src.utils.logger import logging
from src.utils.exception import MRDException
from src.utils.utils import JsonUtils

from datetime import datetime
import os,sys
import json
import time


def run_query(question: str) -> str:
    try:
        schema_retriever = get_vectordb_retriever()
        agent_chain = build_agent_chain(schema_retriever)
    
        logging.info("Invoking agent chain for question: %s", question)
        return agent_chain.invoke({"question": question})
    except Exception as e:
        raise MRDException(e,sys) from e

def testing_test_runner():
    test_cases = JsonUtils.read_json(GOLDEN_DATASET_PATH)
    test_execution_results = []
    for test in test_cases:
        try:
            logging.info(f"Executing Test ID:{test['id']}")
            user_query = test['question']
            answer = run_query(user_query)
            print("\n--- Final Agent Answer ---")
            print(answer['final_answer'])
            evaluation_input = {k: answer[k] for k in ['question', 'sql_script', 'sql_result','sql_llm','summary_llm' ,'final_answer']}
            evaluation_input["sql_llm"].pop("answer", None)
            evaluation_input["summary_llm"].pop("answer", None)
            evaluation_input['id'] = test['id']
            test_execution_results.append(evaluation_input)
            logging.info(f"Test ID:{test['id']} execution completed")
        except Exception as e:
            logging.exception(f"Test ID:{test['id']} failed: {e}")
            continue
        time.sleep(20)
        
    test_artifact_filename = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.json"
    JsonUtils.write_json(os.path.join(TEST_ARTIFACTS_DIR,test_artifact_filename),test_execution_results)
    logging.info("All test executions completed successfully.")

# Server=localhost;Database=master;Trusted_Connection=True;
# sqlcmd -S localhost -C