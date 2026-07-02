"""
Executes LLM-generated SQL against the configured database and returns a
structured, JSON-serializable result. This is the function the LangChain
agent calls after it generates a SQL string.
"""
from typing import Any, Dict
import sys
from src.database.connection import get_cursor
from src.utils.exception import MRDException

def clean_sql(sql_script: str) -> str:
    try:
        """Strips markdown code fences that LLMs often wrap SQL in."""
        return sql_script.replace("```sql", "").replace("```", "").strip()
    except Exception as e:
        raise MRDException(e,sys) from e


def execute_sql_query(sql_script: str) -> Dict[str, Any]:
    """
    Receives a generated SQL query string, executes it, and returns
    {"columns": [...], "rows": [...]}.
    """
    try:
        sql_query = clean_sql(sql_script)
        cursor = get_cursor()
        cursor.execute(sql_query)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        return {
            "columns": columns,
            "rows": [list(row) for row in rows],
        }
    except Exception as e:
        raise MRDException(e,sys) from e