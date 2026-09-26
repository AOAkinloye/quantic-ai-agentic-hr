# HR Agentic Assistant

A production-grade, agentic HR policy and operations web application.

## Overview
This application combines Retrieval-Augmented Generation (RAG) over internal policy documents with Model Context Protocol (MCP) server tools operating over mock employee, PTO, and benefits data.

## Features
- **Interactive Web UI**: Chat interface providing answers with citations and tool execution traces.
- **RAG Pipeline**: Semantic search over markdown policy documents using ChromaDB and SentenceTransformers.
- **MCP Server**: FastMCP implementation exposing tools to query policies, employee profiles, PTO, benefits, and create HR tickets.
- **Agent Orchestrator**: Langchain/LiteLLM based ReAct loop to route queries between RAG and mock data tools.

## Setup Instructions
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Build the RAG index:
   ```bash
   python rag_pipeline.py
   ```
3. Set environment variables (copy `.env.example` to `.env` and fill out your LLM details).
4. Run the web application:
   ```bash
   python main.py
   ```
5. Open `http://localhost:8000` in your browser.

## Deployment
This application is designed for single-service deployment on Render or Railway. 
It uses a local SQLite-backed ChromaDB and local JSON files for mock data to eliminate external paid dependencies.

**Cold Start Warning**: On free tiers (e.g., Render free tier), the application goes to sleep after inactivity. It may take up to 60 seconds to start upon receiving a new request.
