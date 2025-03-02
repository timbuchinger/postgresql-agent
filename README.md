# PostgreSQL Agent

A natural language interface for PostgreSQL databases using AI agents.

## Overview

This project enables natural language querying of PostgreSQL databases by:
1. Analyzing the database schema
2. Converting questions to SQL queries
3. Executing queries and formatting results
4. Providing human-readable answers

## Installation

This project uses UV for dependency management. First, install UV:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install the project dependencies:

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows

uv pip install .          # Install runtime dependencies
uv pip install ".[dev]"   # Install development dependencies
```

## Configuration

The project requires configuration through environment variables:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your configuration:
   ```
   # PostgreSQL Connection Parameters
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_password
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=your_database

   # LiteLLM Configuration
   LITELLM_BASE_URL=https://your.litellm.server
   ```

The connection string will be automatically built using these environment variables. The project defaults to using the Mistral model from Ollama.

## Usage

There are two ways to use this project:

### 1. Interactive CLI

Run the interactive command-line interface:

```bash
python run.py
```

This will start an interactive session where you can:
- Enter questions about your database
- Get AI-generated answers
- Type 'quit' to exit

### 2. As a Python Package

Import and use in your Python code:

```python
from postgresql_agent import PostgresConnector, answer_database_question

# Initialize database connection
db = PostgresConnector()

# Ask a question
question = "What were the top 5 customers by revenue last month?"
answer = answer_database_question(question)
print(answer)
```

## Development

Format code:
```bash
black src/
isort src/
```

Run linters:
```bash
ruff check src/
mypy src/
```

## Project Structure

```
postgresql-agent/
├── src/
│   └── postgresql_agent/
│       ├── __init__.py      # Package exports
│       ├── connector.py     # Database connection
│       ├── agents.py        # AI agent definitions
│       ├── llm.py          # Ollama LLM integration
│       ├── tasks.py         # Task definitions
│       └── tools.py         # Database tools
├── tests/                   # Test files
├── pyproject.toml          # Project configuration
└── README.md              # This file
