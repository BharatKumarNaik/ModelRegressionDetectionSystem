# Input
''' Golden dataset '''
''' Test_Runner output '''
''' Note: Test_Runner output must be on frozen dataset such that it makes sense to evaluate it against golden dataset'''


# Output:
'''
{
    "id":"TC_001",

    "sql_match":1.0,

    "sql_result":0.75,

    "answer_similarity":0.94,

    "latency_pass":false,

    "token_pass":false,

    "passed":false
}
'''

from src.database.query_executor import execute_sql_query
from src.utils.exception import MRDException
from src.utils.logger import logging

class Evaluator:
    def __init__(self,golden_data,testcase_output):
        self.golden_data = golden_data
        self.testcase_output = testcase_output

    def evaluate_sql_script():
        pass
    def evaluate_sql_result():
        pass
    def evaluate_final_answer():
        pass
    def evaluate_latency():
        pass
    def evaluate_tokens():
        pass
    def evaluate_run():
        pass