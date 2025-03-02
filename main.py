from typing import Dict, List

from crewai import Agent, Crew, Process, Task
from langchain.llms import Anthropic
from langchain.tools import Tool

from postgresql_agent.connector import PostgresConnector

# Initialize components
db = PostgresConnector()
llm = Anthropic(model="claude-3-7-sonnet-20250219")

# Define tools
tools = [
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

# Define agents
analyst = Agent(
    role="Database Analyst",
    goal="Understand the database schema and form appropriate SQL queries",
    backstory="Expert in database design and SQL analysis with decades of experience",
    tools=tools,
    llm=llm,
    verbose=True,
)

query_builder = Agent(
    role="SQL Query Builder",
    goal="Build efficient and accurate SQL queries to answer user questions",
    backstory="SQL expert specializing in optimizing complex queries for PostgreSQL",
    tools=tools,
    llm=llm,
    verbose=True,
)

answer_generator = Agent(
    role="Answer Formatter",
    goal="Translate technical database results into clear, human-readable answers",
    backstory="Data interpreter skilled at explaining complex data in simple terms",
    llm=llm,
    verbose=True,
)


# Define tasks
def answer_database_question(question: str) -> str:
    understand_schema = Task(
        description=f"Analyze database schema to understand the data structure relevant to: '{question}'",
        agent=analyst,
        expected_output="A detailed understanding of the relevant tables, columns, and relationships.",
    )

    build_queries = Task(
        description="Build one or more SQL queries to extract the information needed to answer the question",
        agent=query_builder,
        expected_output="Working SQL queries that will extract the necessary data",
        context=lambda: understand_schema.output,
    )

    generate_answer = Task(
        description="Translate the query results into a clear, concise answer to the original question",
        agent=answer_generator,
        expected_output="A human-readable answer to the question based on database results",
        context=lambda: f"Question: {question}\nQueries and Results: {build_queries.output}",
    )

    # Create crew and process tasks
    crew = Crew(
        agents=[analyst, query_builder, answer_generator],
        tasks=[understand_schema, build_queries, generate_answer],
        process=Process.sequential,
    )

    result = crew.kickoff()
    return result


# Sample usage
if __name__ == "__main__":
    question = "What were the top 5 customers by revenue last month?"
    answer = answer_database_question(question)
    print(answer)
