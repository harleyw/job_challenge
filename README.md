# job_challenge

1. Setup
```
    python3 -m venv venv
    source venv/bin/activate
    pip install -r second_stage/requirements.txt
```

2. Challeng Tasks

* First Stage - Basing on https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_adaptive_rag/

    - Starting the service
        ```
        cd first_stage
        python3 app.py
        ```
        The, input url: http://localhost:8000 in the chrome/edge

   - Demo for the first stage
<img width="1479" height="686" alt="屏幕截图 2025-08-11 170842" src="https://github.com/user-attachments/assets/7be5e6ba-e415-4180-a095-4bdeaa1ed0fb" />

* Second Stage - Basing on https://langchain-ai.github.io/langgraph/tutorials/multi_agent/hierarchical_agent_teams/

    - Starting the service
        ```
        cd second_stage
        # Backend service
        python3 server.py

        # Frontend service
        python3 -m http.server 8080
        ```
        
        Then, input url: http://localhost:8080 in the chrome/edge

   - Demo for second stage
   animation: https://github.com/harleyw/job_challenge/blob/main/second_stage/2nd_stage_demo.mp4
   
<img width="1833" height="946" alt="2025-08-18" src="https://github.com/user-attachments/assets/3eef7404-b576-4b50-9002-c20457133309" />
