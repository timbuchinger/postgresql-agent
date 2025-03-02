"""Task definitions for database operations."""

from typing import List

from crewai import Crew, Process, Task

from .agents import analyst, answer_generator, query_builder


def answer_database_question(question: str) -> str:
    """Process a natural language database question and return an answer.

    Args:
        question: Natural language question about the database

    Returns:
        Human-readable answer based on database query results
    """
    understand_schema = Task(
        description=f"Analyze database schema to understand the data structure relevant to: '{question}'",
        agent=analyst,
        expected_output="A detailed understanding of the relevant tables, columns, and relationships.",
        context=[],
    )

    build_queries = Task(
        description="Build one or more SQL queries to extract the information needed to answer the question",
        agent=query_builder,
        expected_output="Working SQL queries that will extract the necessary data",
        context=[understand_schema.output] if understand_schema.output else [],
    )

    generate_answer = Task(
        description="Translate the query results into a clear, concise answer to the original question",
        agent=answer_generator,
        expected_output="A human-readable answer to the question based on database results",
        context=(
            [f"Question: {question}\nQueries and Results: {build_queries.output}"]
            if build_queries.output
            else []
        ),
    )

    crew = Crew(
        agents=[analyst, query_builder, answer_generator],
        tasks=[understand_schema, build_queries, generate_answer],
        process=Process.sequential,
        verbose=True,
    )

    return crew.kickoff()
