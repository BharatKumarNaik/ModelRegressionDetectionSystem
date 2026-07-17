"""
Centralized configuration. All environment-dependent values (DB connection,
model names, retrieval params) live here so nothing else in the codebase
hardcodes them.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Database Configuration ---
DB_DRIVER = os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")
DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_NAME = os.getenv("DB_NAME", "WideWorldImporters")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "yes")
# If you move off Windows trusted auth (recommended for prod), add these:
DB_UID = os.getenv("DB_UID")
DB_PWD = os.getenv("DB_PWD")


def get_connection_string() -> str:
    if DB_UID and DB_PWD:
        return (
            f"DRIVER={DB_DRIVER};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_NAME};"
            f"UID={DB_UID};PWD={DB_PWD};"
        )
    return (
        f"DRIVER={DB_DRIVER};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        f"Trusted_Connection={DB_TRUSTED_CONNECTION};"
    )


# --- LLM / Embedding Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # picked up automatically by the SDK
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-2")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))
RETRIEVER_TOP_K = int(os.getenv("RETRIEVER_TOP_K", "5"))

# Vector DB and Hash store location
VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR", "artifacts/vector_store")
SCHEMA_HASH_PATH = os.getenv("SCHEMA_HASH_PATH", "artifacts/vector_store/schema_hash.txt")

TEST_ARTIFACTS_DIR = "artifacts/test_dir"
GOLDEN_DATASET_PATH = "datasets/golden_dataset.json"
EVALUATION_RESULT_DIR = "artifacts/evaluation"