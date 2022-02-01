"""
Name: orca_sql.py

Description: SQL used for creating the ORCA database.
"""
# Imports
from sqlalchemy import text
from sqlalchemy.sql.elements import TextClause
from orca_shared.database.shared_db import logger


# ----------------------------------------------------------------------------
# ORCA SQL used for creating the Database
# ----------------------------------------------------------------------------


def commit_sql() -> TextClause:
    """
    SQL for a simple 'commit' to exit the current transaction.
    """
    return text("commit")


def app_database_sql(db_name: str) -> TextClause:
    """
    Full SQL for creating the ORCA application database.

    Returns:
        (sqlalchemy.sql.element.TextClause): SQL for creating database.
    """
    return text(
        f"""
        CREATE DATABASE {db_name}
            OWNER postgres
            TEMPLATE template1
            ENCODING 'UTF8';
    """
    )


def app_database_comment_sql(db_name: str) -> TextClause:
    """
    SQL for adding a documentation comment to the database.
    Cannot be merged with DB creation due to SQLAlchemy limitations.
    """
    return text(
        f"""
        COMMENT ON DATABASE {db_name}
            IS 'Operational Recovery Cloud Archive (ORCA) database.'
"""
    )