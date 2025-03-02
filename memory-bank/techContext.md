# Technical Context

## Technologies
- Python 3.x
- CrewAI for agent orchestration and task management
- Groq LLM using llama-3.3-70b-versatile model
- PostgreSQL for database
- psycopg2-binary for database connectivity
- python-dotenv for environment management

## Development Setup
1. Install dependencies from requirements.txt
2. Configure .env file with:
   - GROQ_API_KEY
   - DATABASE_URL

## Technical Constraints
- Single file implementation for simplicity
- Stateless operation (no conversation history)
- Direct database connection without query caching
