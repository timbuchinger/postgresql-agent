import logging
import os
from typing import Optional

import psycopg2
from crewai import LLM, Agent, Crew, Task
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class PostgreSQLAgent:
    """A class to handle PostgreSQL database queries using CrewAI."""

    def __init__(
        self, max_iterations: Optional[int] = 3, max_results: Optional[int] = 100
    ):
        """Initialize the PostgreSQL Agent with configuration.

        Args:
            max_iterations: Maximum number of follow-up queries to execute (default: 3)
            max_results: Maximum number of total results to accumulate (default: 100)
        """
        # Load environment variables
        load_dotenv()

        # Set limits
        self.max_iterations = max_iterations
        self.max_results = max_results

        # Initialize Groq LLM # llama-3.3-70b-versatile
        self.llm = LLM(model="groq/qwen-qwq-32b", temperature=0.7)

        # Create the database agent
        self.agent = self._create_db_agent()

        # Cache for schema information
        self.schema_cache = None

    def _get_db_connection(self):
        """Create a database connection using environment variables."""
        logger.debug("Creating new database connection")
        return psycopg2.connect(
            os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor
        )

    def _create_db_agent(self):
        """Create a CrewAI agent for database querying."""
        return Agent(
            role="Database Query Expert",
            goal="Accurately analyze and query PostgreSQL database, with expertise in schema analysis, table relationships, and data querying using information_schema views",
            backstory="I am an expert in PostgreSQL and data analysis, with deep knowledge of information_schema views for analyzing database structure, foreign key relationships, and table constraints. I break down complex questions into precise queries and combine results for comprehensive answers.",
            llm=self.llm,
            allow_delegation=False,
        )

    def _get_schema_info(self) -> dict:
        """Get database schema information if not cached."""
        if self.schema_cache:
            return self.schema_cache

        schema_query = """
            SELECT
                t.table_name,
                ARRAY_AGG(
                    CONCAT(c.column_name, ' (', c.data_type, ')')
                    ORDER BY c.ordinal_position
                ) as columns
            FROM
                information_schema.tables t
            JOIN
                information_schema.columns c
                ON t.table_name = c.table_name
            WHERE
                t.table_schema = 'public'
            GROUP BY
                t.table_name;
        """

        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(schema_query)
                    schema_results = cur.fetchall()
                    self.schema_cache = {
                        row["table_name"]: row["columns"] for row in schema_results
                    }
                    return self.schema_cache
        except Exception as e:
            print(f"Error fetching schema: {str(e)}")
            return {}

    def _execute_query(self, sql_query: str) -> list:
        """Execute a single SQL query and return results."""
        logger.info(f"Executing SQL query: {sql_query}")
        with self._get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query)
                results = cur.fetchall()
                logger.info(f"Query returned {len(results)} results")
                return results

    def query_database(self, question: str) -> str:
        """Execute database queries iteratively and return results."""
        logger.info(f"Processing question: {question}")
        try:
            # Get schema information first
            schema_info = self._get_schema_info()

            # Initialize accumulated results
            accumulated_results = []

            # Initial query planning crew
            plan_crew = Crew(
                agents=[self.agent],
                tasks=[
                    Task(
                        description=f"""
                        Plan how to answer this question: "{question}"

                        Available tables and their schemas:
                        {schema_info}

                        For queries about table relationships and foreign keys, use this structure
                        (return just the raw SQL without any markdown formatting):

                        SELECT
                            kcu.table_name,
                            kcu.column_name,
                            ccu.table_name AS foreign_table_name,
                            ccu.column_name AS foreign_column_name
                        FROM
                            information_schema.table_constraints AS tc
                            JOIN information_schema.key_column_usage AS kcu
                                ON tc.constraint_name = kcu.constraint_name
                            JOIN information_schema.constraint_column_usage AS ccu
                                ON ccu.constraint_name = tc.constraint_name
                        WHERE tc.constraint_type = 'FOREIGN KEY'

                        1. Formulate an initial PostgreSQL query to gather necessary information
                        2. Return ONLY the SQL query string, nothing else
                        """,
                        agent=self.agent,
                        expected_output="SQL query string",
                    )
                ],
            )

            # Execute initial query
            logger.info("Planning initial query...")
            initial_query = str(plan_crew.kickoff()).strip()
            logger.info("Executing initial query...")
            initial_results = self._execute_query(initial_query)
            accumulated_results.extend(
                initial_results[: self.max_results]
            )  # Limit initial results

            # Track iterations
            iteration_count = 1

            # Evaluation crew to determine if more queries are needed
            while iteration_count < self.max_iterations:
                logger.info(
                    f"Evaluating results (iteration {iteration_count}/{self.max_iterations})..."
                )
                eval_crew = Crew(
                    agents=[self.agent],
                    tasks=[
                        Task(
                            description=f"""
                            Analyze these results for the question: "{question}"

                            Current results: {accumulated_results}
                            Available schema: {schema_info}

                            For queries about table relationships and foreign keys, use this structure
                            (return just the raw SQL without any markdown formatting):

                            SELECT
                                kcu.table_name,
                                kcu.column_name,
                                ccu.table_name AS foreign_table_name,
                                ccu.column_name AS foreign_column_name
                            FROM
                                information_schema.table_constraints AS tc
                                JOIN information_schema.key_column_usage AS kcu
                                    ON tc.constraint_name = kcu.constraint_name
                                JOIN information_schema.constraint_column_usage AS ccu
                                    ON ccu.constraint_name = tc.constraint_name
                            WHERE tc.constraint_type = 'FOREIGN KEY'

                            Determine if additional queries are needed to fully answer the question.
                            If yes, provide ONLY a new SQL query string.
                            If no, respond with "COMPLETE".
                            """,
                            agent=self.agent,
                            expected_output="SQL query string or COMPLETE",
                        )
                    ],
                )

                eval_result = str(eval_crew.kickoff()).strip()

                if eval_result == "COMPLETE":
                    logger.info("Evaluation complete - no more queries needed")
                    break

                # Execute follow-up query
                logger.info("Executing follow-up query...")
                follow_up_results = self._execute_query(eval_result)

                # Check if adding results would exceed limit
                remaining_capacity = self.max_results - len(accumulated_results)
                if remaining_capacity <= 0:
                    logger.warning(f"Result limit reached ({self.max_results} records)")
                    formatted_response = (
                        f"Note: Results limited to {self.max_results} records. "
                        "Consider refining your query to be more specific."
                    )
                    return formatted_response

                accumulated_results.extend(follow_up_results[:remaining_capacity])
                iteration_count += 1

            if iteration_count >= self.max_iterations:
                logger.warning(f"Maximum iterations reached ({self.max_iterations})")
                formatted_response = (
                    f"Note: Query processing limited to {self.max_iterations} iterations. "
                    "Consider refining your query to be more specific."
                )
                return formatted_response

            # Final response formatting
            logger.info("Formatting final response...")
            format_crew = Crew(
                agents=[self.agent],
                tasks=[
                    Task(
                        description=f"""
                        Format these database results into a response:
                        Question: {question}
                        Combined Results: {accumulated_results}

                        Apply one of these formatting templates based on the query type:

                        1. For table schema/structure queries:
                        [table name]
                        - [column name] ([data type])

                        Example:
                        users
                        - id (integer)
                        - email (varchar)
                        - created_at (timestamp)

                        2. For table relationship queries:
                        [table name]
                        Relationships:
                          → [related table] via [column] = [foreign column]
                            Type: [relationship type]

                        Example:
                        stocks
                        Relationships:
                          → price_history via symbol = symbol
                            Type: One-to-Many
                          → stock_news via symbol = symbol
                            Type: One-to-Many

                        3. For data queries:
                        Provide a natural language response that synthesizes the information.

                        Determine the query type from the question and format accordingly.
                        """,
                        agent=self.agent,
                        expected_output="Natural language response",
                    )
                ],
            )

            formatted_response = str(format_crew.kickoff()).strip()
            return formatted_response

        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return f"Error: {str(e)}"


def main():
    """Main function to handle user queries through CLI."""
    logger.info("Starting PostgreSQL Agent CLI")
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
