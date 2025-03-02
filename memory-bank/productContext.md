# Product Context

## Purpose
The PostgreSQL Query Agent serves as a natural language interface to PostgreSQL databases, enabling users to interact with their data using plain English questions rather than SQL queries.

## Problems Solved
1. Technical Barrier: Eliminates the need for users to know SQL syntax
2. Query Complexity: Handles the translation of complex questions into proper SQL
3. Response Formatting: Presents database results in human-readable format

## How It Works
1. User provides a natural language question about their database
2. Agent uses CrewAI to:
   - Parse the question and generate appropriate SQL query
   - Execute the query against the PostgreSQL database
   - Format results into clear, natural language responses
3. Special handling for schema-related queries with structured output format

## User Experience Goals
- Simple command-line interface
- Quick response times
- Clear, understandable answers
- Consistent formatting for schema information
- Graceful error handling with user-friendly messages

## Target Users
- Database administrators needing quick data insights
- Non-technical users requiring database access
- Developers during database exploration and testing
