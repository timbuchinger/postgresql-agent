import os
from typing import Optional

import psycopg2
from crewai import LLM, Agent, Crew, Task
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


class PostgreSQLAgent:
    """A class to handle PostgreSQL database queries using CrewAI."""

    def __init__(self):
        """Initialize the PostgreSQL Agent with configuration."""
        # Load environment variables
        load_dotenv()

        # Initialize Groq LLM
        self.llm = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.7)

        # Create the database agent
        self.agent = self._create_db_agent()

    def _get_db_connection(self):
        """Create a database connection using environment variables."""
        return psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)

    def _create_db_agent(self):
        """Create a CrewAI agent for database querying."""
        return Agent(
            role="Database Query Expert",
            goal="Accurately query PostgreSQL database and provide clear answers",
            backstory="I am an expert in SQL and data analysis, skilled at translating natural language questions into SQL queries.",
            llm=self.llm,
            allow_delegation=False,
        )

    def query_database(self, question: str) -> str:
        """Execute database query and return results."""
        crew = Crew(
            agents=[self.agent],
            tasks=[
                Task(
                    description=f"""
                    Based on the question: "{question}"
                    1. Formulate an appropriate PostgreSQL query
                    2. Return ONLY the SQL query string, nothing else
                    """,
                    agent=self.agent,
                    expected_output="SQL query string",
                )
            ],
        )

        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Get the SQL query from the agent and ensure it's a string
                    crew_output = crew.kickoff()
                    sql_query = str(crew_output).strip()

                    # Execute the query
                    cur.execute(sql_query)
                    results = cur.fetchall()

                    # Create a new crew for formatting the response
                    format_crew = Crew(
                        agents=[self.agent],
                        tasks=[
                            Task(
                                description=f"""
                                Format these database results into a response:
                                Question: {question}
                                Results: {results}

                                If the query is about table schema/structure, format the output exactly as:
                                [table name]
                                - [column name] ([data type])

                                Example format:
                                users
                                - id (integer)
                                - email (varchar)
                                - created_at (timestamp)

                                For non-schema queries, provide a natural language response.
                                """,
                                agent=self.agent,
                                expected_output="Natural language response",
                            )
                        ],
                    )
                    formatted_response = str(format_crew.kickoff()).strip()
                    return formatted_response

        except Exception as e:
            return f"Error: {str(e)}"


def main():
    """Main function to handle user queries through CLI."""
    agent = PostgreSQLAgent()

    while True:
        question = input("\nEnter your question (or 'quit' to exit): ")
        if question.lower() in ["quit", "exit", "q"]:
            break

        print("\nProcessing your question...")
        response = agent.query_database(question)
        print(f"\nResponse: {response}")


if __name__ == "__main__":
    main()
