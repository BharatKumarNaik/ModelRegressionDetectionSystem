'''
load golden dataset -> call model for each question -> collect and save the result
'''
'''
{
id: "TC_001",
question:"",
sql_script:"",
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

    evaluation_input = {k: answer[k] for k in ['question', 'sql_script', 'sql_result','sql_llm','summary_llm' ,'final_answer']}
    evaluation_input["sql_llm"].pop("answer", None)
    evaluation_input["summary_llm"].pop("answer", None)
    print(evaluation_input['sql_llm'])
    print(evaluation_input['summary_llm'])


# Server=localhost;Database=master;Trusted_Connection=True;
# sqlcmd -S localhost -C