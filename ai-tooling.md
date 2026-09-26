# AI Tooling Documentation

## Tools Used During Development
- **Google Deepmind Antigravity**: Used as the primary agentic pair-programmer to scaffold, generate, and orchestrate the project structure.
- **LiteLLM**: Standardized LLM completions API, enabling easy switching between OpenAI, Groq, OpenRouter, and Gemini for the agent orchestrator.
- **SentenceTransformers**: Used `all-MiniLM-L6-v2` for free, local embeddings to avoid API costs during evaluation and deployment.
- **Model Context Protocol (MCP)**: Utilized the official `mcp` Python SDK (specifically `FastMCP` and `stdio_client`) to seamlessly expose python functions as formal MCP tools.

## What Worked Well
- The `FastMCP` class makes defining tools extremely simple using decorators, abstracting away the complex JSON-RPC setup.
- Combining local ChromaDB with HuggingFace embeddings provided a robust and completely free RAG pipeline.

## Challenges Encountered
- **MCP Transport**: Managing subprocesses for `stdio` transport within a single web service can be tricky, especially regarding graceful shutdowns. Using `AsyncExitStack` ensures the subprocess is terminated correctly when the FastAPI app shuts down.
- **Agent Loop**: Implementing a robust tool-calling loop requires careful parsing of tool arguments (handling JSON decoding errors) and appending correct message roles (tool calls and tool results) for the LLM context window.
