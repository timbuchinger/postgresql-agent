# Agent Selection Plan

## Overview
Implementation plan for transforming the PostgreSQL Query Assistant into a multi-agent platform that allows users to select and interact with different specialized agents through a unified interface.

## Configuration Structure

### Agent Registry
```python
class BaseAgent:
    def __init__(self):
        self.name = None
        self.description = None
        
    def query(self, question: str) -> str:
        raise NotImplementedError
        
    def get_examples(self) -> List[str]:
        raise NotImplementedError
        
    def get_predefined_prompts(self) -> List[str]:
        raise NotImplementedError

# Example concrete implementation
class PostgreSQLAgent(BaseAgent):
    def __init__(self):
        self.name = "PostgreSQL Query Agent"
        self.description = "Natural language interface for PostgreSQL databases"
```

## Selection Flow
```mermaid
flowchart TD
    A[App Start] --> B[Load Agent Registry]
    B --> C[Display Agent Selection]
    C --> D{Agent Selected?}
    D -->|Yes| E[Initialize Agent]
    E --> F[Load Agent Config]
    F --> G[Show Agent Interface]
    G --> H{New Agent Selected?}
    H -->|Yes| E
    H -->|No| I[Process Query]
    I --> G
```

## Implementation Details

### Required Changes

1. Agent Registry System:
```python
class AgentRegistry:
    def __init__(self):
        self._agents = {}
        
    def register(self, agent_class: Type[BaseAgent]):
        instance = agent_class()
        self._agents[instance.name] = agent_class
        
    def get_agent(self, name: str) -> BaseAgent:
        return self._agents[name]()
        
    def list_agents(self) -> List[str]:
        return list(self._agents.keys())
```

2. Environment Variables:
```bash
# Per-agent configuration
POSTGRES_AGENT_DB_URL=postgresql://user:pass@host:port/db
OTHER_AGENT_API_KEY=your-api-key
```

### UI Components

1. Agent Selection:
```python
def render_agent_selector():
    agents = registry.list_agents()
    selected = st.selectbox(
        "Select Agent:",
        agents,
        format_func=lambda x: registry.get_agent(x).description
    )
    return selected
```

2. Dynamic Interface:
```python
def show_agent_interface(agent: BaseAgent):
    st.title(agent.name)
    
    # Dynamic examples
    st.markdown("### Example Questions")
    for example in agent.get_examples():
        st.markdown(f"- {example}")
    
    # Agent-specific prompts
    prompts = agent.get_predefined_prompts()
    if prompts:
        selected = st.selectbox(
            "Predefined Prompts:",
            ["Select a prompt..."] + prompts
        )
```

### State Management

1. Session State:
```python
def initialize_state():
    if "current_agent" not in st.session_state:
        st.session_state.current_agent = None
    if "agent_config" not in st.session_state:
        st.session_state.agent_config = {}
```

2. Agent Configuration:
```python
def load_agent_config(agent_name: str):
    return {
        "PostgreSQL Query Agent": {
            "db_url": os.getenv("POSTGRES_AGENT_DB_URL"),
            "max_results": 1000
        },
        # Other agent configurations...
    }.get(agent_name, {})
```

## Future Enhancements

1. Agent Management:
   - Dynamic agent loading/unloading
   - Agent settings customization
   - Agent performance metrics

2. User Preferences:
   - Default agent selection
   - Custom predefined prompts
   - Result format preferences

3. Integration Features:
   - Cross-agent queries
   - Agent chaining
   - Result comparison between agents

4. Security:
   - Agent-specific access control
   - Resource usage limits
   - Query validation per agent

5. UI Improvements:
   - Agent-specific themes
   - Custom visualization options
   - Keyboard shortcuts

## Implementation Steps

1. Core Changes:
   - Create BaseAgent class
   - Implement AgentRegistry
   - Convert PostgreSQLAgent

2. UI Updates:
   - Add agent selector
   - Create dynamic interface
   - Update response handling

3. Configuration:
   - Setup agent configs
   - Environment variables
   - State management

4. Testing:
   - Agent switching
   - Configuration loading
   - Error handling

5. Documentation:
   - Update README
   - Add agent development guide
   - Document configuration options
