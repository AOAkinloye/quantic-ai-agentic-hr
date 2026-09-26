# Design and Evaluation

## Architecture
The application uses a FastAPI backend with a simple HTML frontend. 
- **Agent Orchestrator**: Uses an async ReAct loop (`agent.py`) via `litellm` calling `acompletion`.
- **MCP Server**: Implemented with `mcp.server.fastmcp`. It exposes 5 tools.
- **RAG Pipeline**: `rag_pipeline.py` uses Langchain to parse, chunk, embed (`all-MiniLM-L6-v2`), and index documents in ChromaDB.

## MCP Schema
The MCP server exposes:
1. `search_policy_documents`: query (string), k (int)
2. `lookup_employee_profile`: employee_id (string)
3. `check_pto_balance`: employee_id (string)
4. `lookup_benefits_status`: employee_id (string)
5. `create_mock_hr_ticket`: employee_id (string), request_type (string), description (string)

## Safety Mechanisms
The agent is instructed not to perform real state-modifying actions without caution. The `create_mock_hr_ticket` tool explicitly operates on a mock local JSON file (`tickets.json`), ensuring safety.

## Evaluation
An evaluation script (`evaluation/run_eval.py`) runs the agent against 20 test cases covering multi-doc RAG, tool-use, and ambiguous questions.
Metrics captured:
- **Tool Selection Accuracy**: Percentage of correct tool calls.
- **Answer Accuracy**: Checking for presence of expected snippet in the response.
- **Average Latency**: To monitor performance, especially useful for tracking cold start vs warm start latency.
