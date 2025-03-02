"""Tests for PostgreSQL connector."""

import json

import pytest

from postgresql_agent.connector import PostgresConnector


@pytest.fixture
def mock_connection(mocker):
    """Mock database connection."""
    mock_cursor = mocker.MagicMock()
    mock_conn = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mocker.patch("psycopg2.connect", return_value=mock_conn)
    return mock_conn, mock_cursor


def test_execute_query_success(mock_connection):
    """Test successful query execution."""
    mock_conn, mock_cursor = mock_connection
    mock_cursor.description = [("column1",), ("column2",)]
    mock_cursor.fetchall.return_value = [(1, "value1"), (2, "value2")]

    connector = PostgresConnector("postgresql://test:test@localhost:5432/test")
    result = connector.execute_query("SELECT * FROM test")

    expected = json.dumps(
        [{"column1": 1, "column2": "value1"}, {"column1": 2, "column2": "value2"}],
        default=str,
    )

    assert result == expected
    mock_cursor.execute.assert_called_once_with("SELECT * FROM test")


def test_execute_query_error(mock_connection):
    """Test query execution error handling."""
    mock_conn, mock_cursor = mock_connection
    mock_cursor.execute.side_effect = Exception("Test error")

    connector = PostgresConnector("postgresql://test:test@localhost:5432/test")
    result = connector.execute_query("SELECT * FROM test")

    assert result == "Error executing query: Test error"
    mock_cursor.execute.assert_called_once_with("SELECT * FROM test")


def test_close_connection(mock_connection):
    """Test connection cleanup."""
    mock_conn, mock_cursor = mock_connection

    connector = PostgresConnector("postgresql://test:test@localhost:5432/test")
    connector.close()

    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
