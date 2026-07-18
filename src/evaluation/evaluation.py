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
from src.config.settings import LLM_MODEL
from src.utils.utils import JsonUtils
from pathlib import Path
from datetime import datetime
from src.config.settings import TEST_ARTIFACTS_DIR,GOLDEN_DATASET_PATH,EVALUATION_RESULT_DIR
from thefuzz import fuzz
from deepeval.models import GeminiModel
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
import os,time
from dotenv import load_dotenv
load_dotenv()

judge = GeminiModel(
    model=LLM_MODEL,
    api_key=os.getenv("GOOGLE_API_KEY"),
)

metric = AnswerRelevancyMetric(
    model=judge
)

class Evaluator:
    def evaluate_sql_script(self,query1,query2):
        # Ignores duplicate/common tokens and compares the unique token sets (0-100); useful when one SQL query contains extra conditions or columns.
        return fuzz.token_set_ratio(query1, query2)/100
    
    def evaluate_final_answer(self,question,answer1,answer2):
        test_case = LLMTestCase(
        input=question,
        actual_output=answer1,
        expected_output=answer2
        )
        metric.measure(test_case)
        score = metric.score
        # logging.info(f"DeepEval metric score:{score}")
        # logging.info(f"DeepEval metric reason:{metric.reason}")
        # logging.info(f"DeepEval metric success:{metric.success}")
        return score

    def evaluate_sql_result(self,result1, result2):
        columns_match = result1["columns"] == result2["columns"]

        row_count_match = len(result1["rows"]) == len(result2["rows"])

        data_match = sorted(result1["rows"]) == sorted(result2["rows"])

        score = (
            0.2 * columns_match +
            0.2 * row_count_match +
            0.6 * data_match
        )

        return {
            "score": score,
            "columns_match": columns_match,
            "row_count_match": row_count_match,
            "data_match": data_match
        }
    def evaluate_latency(self,current, baseline):
        delta = current - baseline
        percent_change = (delta / baseline) * 100 if baseline else 0
        return {
            "current": current,
            "baseline": baseline,
            "delta_ms": delta,
            "percent_change": percent_change
        }
    
    def evaluate_tokens(self,current, baseline):
        delta = current - baseline
        percent_change = (delta / baseline) * 100 if baseline else 0
        return {
            "current": current,
            "baseline": baseline,
            "delta_tokens": delta,
            "percent_change": percent_change
        }
    
    def evaluate_run(self,golden_dataset, latest_test_artifact):
        evaluation_results = []
        for golden, latest in zip(golden_dataset, latest_test_artifact):
            sql_match = self.evaluate_sql_script(
                golden["sql_script"],
                latest["sql_script"]
            )
            sql_result_eval = self.evaluate_sql_result(
                golden["sql_result"],
                latest["sql_result"]
            )
            answer_similarity = self.evaluate_final_answer(
                golden["question"],
                latest["final_answer"],
                golden["final_answer"]
            )

            latency_eval = self.evaluate_latency(
                latest["summary_llm"]["latency_ms"],
                2035
            )

            token_eval = self.evaluate_tokens(
                latest["summary_llm"]["total_tokens"],
                12260
            )

            latency_pass = latency_eval["percent_change"] <= 20
            token_pass = token_eval["percent_change"] <= 20
            passed = (
                sql_match >= 0.90 and
                sql_result_eval["score"] >= 0.90 and
                answer_similarity >= 0.90 and
                latency_pass and
                token_pass
            )
            evaluation_results.append(
                {
                    "id": latest["id"],
                    "sql_match": round(sql_match, 2),
                    "sql_result": round(sql_result_eval["score"], 2),
                    "answer_similarity": round(answer_similarity, 2),
                    "latency_pass": latency_pass,
                    "token_pass": token_pass,
                    "passed": passed
                }
            )
            time.sleep(20)
        return evaluation_results

'''
{
    "id":"TC_010",

    "sql_match":{
        "baseline":0.93,
        "current":0.81,
        "delta":-0.12,
        "regression":true
    },

    "answer_similarity":{
        "baseline":0.96,
        "current":1.00,
        "delta":0.04,
        "regression":false
    },

    "latency":{
        "baseline":true,
        "current":false,
        "regression":true
    },

    "tokens":{
        "baseline":true,
        "current":true,
        "regression":false
    }
}
'''
class Regressor:
    def __init__(self, previous_artifact, current_artifact):
        """
        previous_artifact : List[Dict]
        current_artifact  : List[Dict]
        """
        self.previous_artifact = {
            item["id"]: item
            for item in previous_artifact
        }
        self.current_artifact = {
            item["id"]: item
            for item in current_artifact
        }

        # Thresholds
        self.SQL_THRESHOLD = -0.05
        self.SQL_RESULT_THRESHOLD = -0.05
        self.ANSWER_THRESHOLD = -0.05

    def generateRegressionReport(self):
        regression_report = []
        common_ids = (
            self.previous_artifact.keys()
            & self.current_artifact.keys()
        )
        for test_id in common_ids:
            previous = self.previous_artifact[test_id]
            current = self.current_artifact[test_id]
            sql_delta = current["sql_match"] - previous["sql_match"]

            sql_result_delta = (
                current["sql_result"]
                - previous["sql_result"]
            )

            answer_delta = (
                current["answer_similarity"]
                - previous["answer_similarity"]
            )

            regression = {

                "id": test_id,

                "sql_match": {
                    "baseline": previous["sql_match"],
                    "current": current["sql_match"],
                    "delta": round(sql_delta, 2),
                    "regression": sql_delta < self.SQL_THRESHOLD
                },

                "sql_result": {
                    "baseline": previous["sql_result"],
                    "current": current["sql_result"],
                    "delta": round(sql_result_delta, 2),
                    "regression": sql_result_delta < self.SQL_RESULT_THRESHOLD
                },

                "answer_similarity": {
                    "baseline": previous["answer_similarity"],
                    "current": current["answer_similarity"],
                    "delta": round(answer_delta, 2),
                    "regression": answer_delta < self.ANSWER_THRESHOLD
                },

                "latency": {
                    "baseline": previous["latency_pass"],
                    "current": current["latency_pass"],
                    "regression":
                        previous["latency_pass"]
                        and not current["latency_pass"]
                },

                "tokens": {
                    "baseline": previous["token_pass"],
                    "current": current["token_pass"],
                    "regression":
                        previous["token_pass"]
                        and not current["token_pass"]
                },

                "overall_regression": False
            }

            regression["overall_regression"] = any([
                regression["sql_match"]["regression"],
                regression["sql_result"]["regression"],
                regression["answer_similarity"]["regression"],
                regression["latency"]["regression"],
                regression["tokens"]["regression"]
            ])

            regression_report.append(regression)

        return regression_report


class Runner:
    def evaluationRunner():
        eval_files = Path(EVALUATION_RESULT_DIR).glob("*.json")
        prev_evalFile = max(eval_files, key=lambda f: f.stat().st_mtime)

        golden_dataset = JsonUtils.read_json(GOLDEN_DATASET_PATH)
        files = Path(TEST_ARTIFACTS_DIR).glob("*.json")
        latest = max(files, key=lambda f: f.stat().st_mtime)
        latest_test_artifact = JsonUtils.read_json(latest)
        Eval = Evaluator()
        evaluation_dict = Eval.evaluate_run(golden_dataset,latest_test_artifact)
        print(evaluation_dict)
        eval_artifact_filename = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.json"
        JsonUtils.write_json(os.path.join(EVALUATION_RESULT_DIR,eval_artifact_filename),evaluation_dict)
        logging.info("All evaluation completed successfully.")

        logging.info("Initiating Regression")
        eval_files = Path(EVALUATION_RESULT_DIR).glob("*.json")
        latest_evalFile = max(files, key=lambda f: f.stat().st_mtime)

        # prev_evalFile=r'artifacts\evaluation\07_16_2026_23_11_47.json'
        # latest_evalFile=r'artifacts\evaluation\07_17_2026_23_11_47.json'
        prev_eval_artifact = JsonUtils.read_json(prev_evalFile)
        latest_eval_artifact = JsonUtils.read_json(latest_evalFile)
        RegGen = Regressor(prev_eval_artifact,latest_eval_artifact)
        RegReport = RegGen.generateRegressionReport()
        logging.info("Regression report is ready")
        return RegReport