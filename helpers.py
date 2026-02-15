"""Helper methods for the flask app."""

import sqlite3
from sqlite3 import Connection, Cursor

from environment import DATABASE


def db_query(query: str, *, params: tuple | None = None) -> tuple[Connection, Cursor]:
    """Connect and executes query against database.

    Args:
        query (str): SQL queryDB
        params (tuple | None): parameters to inject into SQL query. Defaults to None

    Returns:
        tuple[Connection, Cursor]: connection and cursor objects for the database
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, params) if params else cursor.execute(query)
    return conn, cursor


def db_write_query(query: str, *, params: tuple | None = None) -> None:
    """Execute the provided SQL write query against the database.

    Args:
        query (str): SQL write query
        params (tuple | None): parameters to inject into SQL query. Default to None
    """
    conn, _ = db_query(query, params=params)
    conn.commit()
    conn.close()


def db_read_query(query: str, *, params: tuple | None = None) -> tuple[str, str, str, str, str, str]:
    """Return results of SQL read query executed against the database.

    Args:
        query (str): SQL read query
        params (tuple | None): parameters to inject into SQL query. Default to None

    Returns:
        Any: Results of the SQL read query
    """
    conn, cursor = db_query(query, params=params)
    info = cursor.fetchone()
    conn.close()
    return info or ("", "", "", "", "", "")
