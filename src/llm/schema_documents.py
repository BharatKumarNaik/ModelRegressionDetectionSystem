"""
Converts raw schema + relationship metadata (from database/schema_extractor)
into one LangChain Document per table, ready to be embedded.
"""
from typing import Any, Dict, List

import pandas as pd
import sys
from langchain_core.documents import Document
from src.utils.logger import logging
from src.utils.exception import MRDException


def build_schema_documents(
    database_schema: Dict[str, Any],
    relationships: Dict[str, Any],
) -> List[Document]:
    try:
        df_columns = pd.DataFrame(database_schema["rows"], columns=database_schema["columns"])
        df_relations = pd.DataFrame(relationships["rows"], columns=relationships["columns"])

        df_columns["table_key"] = df_columns["TABLE_SCHEMA"] + "." + df_columns["TABLE_NAME"]

        documents: List[Document] = []

        for table_key, group in df_columns.groupby("table_key"):
            columns_str = "\n".join(
                f"  - {row['COLUMN_NAME']} ({row['DATA_TYPE']}, Nullable={row['IS_NULLABLE']})"
                for _, row in group.iterrows()
            )

            rel_subset = df_relations[
                (df_relations["SchemaName"] + "." + df_relations["TableName"]) == table_key
            ]
            pks = ", ".join(rel_subset["PrimaryKeyColumn"].dropna().unique())
            fks = ", ".join(rel_subset["ForeignKeyColumn"].dropna().unique())

            page_content = f"Table Context: {table_key}\n"
            if pks:
                page_content += f"Primary Keys: {pks}\n"
            if fks:
                page_content += f"Foreign Keys: {fks}\n"
            page_content += f"Columns:\n{columns_str}"

            documents.append(Document(page_content=page_content, metadata={"table_name": table_key}))
        logging.info("Vector DB documents are ready")
        return documents
    except Exception as e:
        raise MRDException(e,sys) from e