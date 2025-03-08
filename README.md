# PostgreSQL Query Agent

A Python-based agent that uses CrewAI and Groq LLM to query PostgreSQL databases and provide natural language responses to user questions.

## Features

- Natural language to SQL query conversion
- PostgreSQL database connectivity
- Groq LLM integration using llama-3.3-70b-versatile model
- Simple command-line interface
- Streamlit web interface
- Environment-based configuration
- Stateless operation

## Installation

1. Clone the repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Setup

Create a `.env` file in the project root with the following variables:
```
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://user:password@host:port/database
```

## Usage

### Command Line Interface
Run the agent directly from the command line:
```bash
python agent.py
```

### Web Interface
Launch the Streamlit web application:
```bash
streamlit run streamlit_app.py
```
