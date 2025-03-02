"""AI agents for database operations."""

import os
from typing import Optional

from crewai import Agent
from dotenv import load_dotenv
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

from .connector import PostgresConnector
from .tools import create_database_tools


def create_agents(
    tools: list[Tool], llm: Optional[ChatOpenAI] = None
) -> tuple[Agent, Agent, Agent]:
    """Create AI agents for database operations.

    Args:
        tools: List of database tools
        llm: Language model instance, defaults to configured model

    Returns:
        Tuple of (analyst, query_builder, answer_generator) agents
    """

    analyst = Agent(
        role="Database Analyst",
        goal="Understand the database schema and form appropriate SQL queries",
        backstory="Expert in database design and SQL analysis with decades of experience",
        tools=tools,
        llm=llm,
        allow_delegation=False,
        memory=False,
    )

    query_builder = Agent(
        role="SQL Query Builder",
        goal="Build efficient and accurate SQL queries to answer user questions",
        backstory="SQL expert specializing in optimizing complex queries for PostgreSQL",
        tools=tools,
        llm=llm,
        allow_delegation=False,
        memory=False,
    )

    answer_generator = Agent(
        role="Answer Formatter",
        goal="Translate technical database results into clear, human-readable answers",
        backstory="Data interpreter skilled at explaining complex data in simple terms",
        llm=llm,
        allow_delegation=False,
        memory=False,
    )

    return analyst, query_builder, answer_generator


# Load environment variables
load_dotenv()

# Create database connection and tools
db = PostgresConnector()
tools = create_database_tools(db)

# Initialize agents with tools
llm = ChatOpenAI(
    api_key=os.environ.get("LITELLM_API_KEY"),
    base_url="https://litellm.buchinger.ca/v1",
    model="groq-qwen-2.5-32b",
    max_tokens=4000,
    temperature=0.1,
)
analyst, query_builder, answer_generator = create_agents(tools=tools, llm=llm)
