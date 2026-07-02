"""
Single source of truth for the pyodbc connection. Everything else in
`database/` and `llm/` pulls a cursor from here instead of opening its
own connection.
"""
import pyodbc
from src.config.settings import get_connection_string
from src.utils.exception import MRDException
import sys

_connection: pyodbc.Connection | None = None


def get_connection() -> pyodbc.Connection:
    try:
        global _connection
        if _connection is None:
            _connection = pyodbc.connect(get_connection_string())
        return _connection
    except Exception as e:
        raise MRDException(e,sys) from e


def get_cursor() -> pyodbc.Cursor:
    return get_connection().cursor()


def close_connection() -> None:
    try:
        """Call on app shutdown to release the connection cleanly."""
        global _connection
        if _connection is not None:
            _connection.close()
            _connection = None
    except Exception as e:
        raise MRDException(e,sys) from e
