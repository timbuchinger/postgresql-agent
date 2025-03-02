"""Tools for database operations."""

from langchain.tools import Tool

from .connector import PostgresConnector


def create_database_tools(db: PostgresConnector) -> list[Tool]:
    """Create tools for database operations.

    Args:
        db: PostgreSQL connector instance

    Returns:
        List of tools for database operations
    """
    return [
        Tool(
            name="execute_sql",
            func=db.execute_query,
            description="Execute a SQL query on the Postgres database and return the results as JSON",
        ),
        Tool(
            name="get_schema",
            func=db.get_schema,
            description="Retrieve the database schema showing tables, columns and data types",
        ),
    ]
