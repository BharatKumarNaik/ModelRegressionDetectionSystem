"""
Extracts database schema metadata (columns + PK/FK relationships). This is
the raw material that llm/schema_documents.py turns into retrievable
Document objects for the vector store.
"""
from typing import Any, Dict

from src.database.connection import get_cursor

COLUMNS_QUERY = """
    SELECT
        TABLE_SCHEMA,
        TABLE_NAME,
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        CHARACTER_MAXIMUM_LENGTH,
        ORDINAL_POSITION
    FROM INFORMATION_SCHEMA.COLUMNS
    ORDER BY
        TABLE_SCHEMA,
        TABLE_NAME,
        ORDINAL_POSITION
"""

RELATIONSHIPS_QUERY = """
    SELECT
        s.name AS SchemaName,
        t.name AS TableName,
        pk_col.name AS PrimaryKeyColumn,
        fk_col.name AS ForeignKeyColumn
    FROM sys.tables t
    JOIN sys.schemas s
        ON t.schema_id = s.schema_id
    LEFT JOIN sys.key_constraints pk
        ON t.object_id = pk.parent_object_id
       AND pk.type = 'PK'
    LEFT JOIN sys.index_columns ic
        ON pk.parent_object_id = ic.object_id
       AND pk.unique_index_id = ic.index_id
    LEFT JOIN sys.columns pk_col
        ON ic.object_id = pk_col.object_id
       AND ic.column_id = pk_col.column_id
    LEFT JOIN sys.foreign_key_columns fkc
        ON t.object_id = fkc.parent_object_id
    LEFT JOIN sys.columns fk_col
        ON fkc.parent_object_id = fk_col.object_id
       AND fkc.parent_column_id = fk_col.column_id
    ORDER BY
        s.name,
        t.name
"""


def _run_query(query: str) -> Dict[str, Any]:
    cursor = get_cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    return {"columns": columns, "rows": [list(row) for row in rows]}


def get_database_schema() -> Dict[str, Any]:
    """Column-level metadata for every table in the database."""
    return _run_query(COLUMNS_QUERY)


def get_table_relationships() -> Dict[str, Any]:
    """Primary/foreign key relationship metadata for every table."""
    return _run_query(RELATIONSHIPS_QUERY)
