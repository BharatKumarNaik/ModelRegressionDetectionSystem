# Vector DB Index Manager
import hashlib
import json
from typing import Any, Dict
import os,sys

from src.llm.schema_documents import build_schema_documents
from src.llm.vector_store import build_vector_store, get_schema_retriever
from src.database.schema_extractor import get_database_schema, get_table_relationships
from src.llm.vector_store import load_vector_store,save_vector_store
from src.config.settings import SCHEMA_HASH_PATH, VECTOR_STORE_DIR
from src.utils.exception import MRDException
from src.utils.logger import logging

def _read_stored_hash(path: str = SCHEMA_HASH_PATH) -> str | None:
    try:
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            return f.read().strip()
    except Exception as e:
        raise MRDException(e,sys) from e

def _write_stored_hash(schema_hash: str, path: str = SCHEMA_HASH_PATH) -> None:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(schema_hash)
    except Exception as e:
        raise MRDException(e,sys) from e

def vector_store_exists(path: str = VECTOR_STORE_DIR) -> bool:
    return os.path.exists(os.path.join(path, "index.faiss")) and os.path.exists(
        os.path.join(path, "index.pkl")
    )

def compute_schema_hash(database_schema: Dict[str, Any], relationships: Dict[str, Any]) -> str:
    """
    Hashes the *content* of both result sets (not object identity), so the
    same schema always produces the same hash regardless of dict ordering.
    Row order from SQL Server is deterministic here because both queries
    use ORDER BY, but we sort again defensively before hashing.
    """
    try:
        schema_rows = sorted(tuple(row) for row in database_schema["rows"])
        relationship_rows = sorted(tuple(row) for row in relationships["rows"])

        payload = {
            "schema_columns": database_schema["columns"],
            "schema_rows": schema_rows,
            "relationship_columns": relationships["columns"],
            "relationship_rows": relationship_rows,
        }

        # default=str handles any non-JSON-native types (e.g. Decimal) safely
        serialized = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    except Exception as e:
        raise MRDException(e,sys) from e

def get_vectordb_retriever():
    '''
    Check if Hash of queried data exists or not.
    If exists return the stored vector db->retriever
    Else: create new vector db and store both new hash and vector db and return the retriever
    '''
    try:
        database_schema = get_database_schema()
        relationships = get_table_relationships()
        cur_hash_index = compute_schema_hash(database_schema,relationships)
        prev_hash_index = _read_stored_hash()

        hash_exist = (cur_hash_index is not None
                    and vector_store_exists()
                        and cur_hash_index == prev_hash_index)
        
        if hash_exist:
            logging.info("Schema unchanged (hash match) — reusing existing vector store")
            vector_db=load_vector_store()
            schema_retriever = get_schema_retriever(vector_db)
            return schema_retriever

        logging.info("Rebuilding the VectorDB")
        documents = build_schema_documents(database_schema, relationships)
        vector_db = build_vector_store(documents)
        save_vector_store(vector_db)
        _write_stored_hash(cur_hash_index)
        schema_retriever = get_schema_retriever(vector_db)
        return schema_retriever
    except Exception as e:
        raise MRDException(e,sys) from e