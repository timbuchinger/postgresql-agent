"""PostgreSQL database connector module."""

import json
import os
from typing import Dict, List

import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class PostgresConnector:
    """Manages PostgreSQL database connections and query execution."""

    def __init__(self):
        """Initialize PostgreSQL connector."""
        self.conn_string = self._build_connection_string()
        self.conn = None
        self.cursor = None
        self.connect()

    def _build_connection_string(self) -> str:
        """Build PostgreSQL connection string from environment variables.

        Returns:
            str: PostgreSQL connection string

        Raises:
            ValueError: If required environment variables are missing
        """
        required_vars = [
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "POSTGRES_DB",
        ]

        # Check for missing environment variables
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        return (
            f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
            f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/"
            f"{os.getenv('POSTGRES_DB')}"
        )

    def connect(self) -> None:
        """Establish database connection."""
        self.conn = psycopg2.connect(self.conn_string)
        self.cursor = self.conn.cursor()

    def execute_query(self, query: str) -> str:
        """Execute SQL query and return results as JSON.

        Args:
            query: SQL query to execute

        Returns:
            JSON string containing query results or error message
        """
        try:
            self.cursor.execute(query)
            columns = [desc[0] for desc in self.cursor.description]
            results = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            return json.dumps(results, default=str)
        except Exception as e:
            return f"Error executing query: {str(e)}"

    def get_schema(self) -> str:
        """Retrieve database schema information.

        Returns:
            JSON string containing schema information
        """
        schema_query = """
        SELECT
            table_name,
            column_name,
            data_type
        FROM
            information_schema.columns
        WHERE
            table_schema = 'public'
        ORDER BY
            table_name,
            ordinal_position;
        """
        return self.execute_query(schema_query)

    def close(self) -> None:
        """Close database connection and cursor."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
