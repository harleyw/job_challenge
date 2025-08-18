# job_challenge

1. Setup
```
    python3 -m venv venv
    source venv/bin/activate
    pip install -r second_stage/requirements.txt
```

2. Challeng Tasks

    **First Stage**
    Basing on https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_adaptive_rag/
    Starting server
    ```
    cd first_stage
    python3 app.py
    ```
    Input url: http://localhost:8000 in the chrome/edge

    **Second Stage**
    Basing on https://langchain-ai.github.io/langgraph/tutorials/multi_agent/hierarchical_agent_teams/
    Starting server
    ```
    cd second_stage
    # Backend service
    python3 server.py

    # Frontend service
    python3 -m http.server 8080
    ```
    Input url: http://localhost:8080 in the chrome/edge
