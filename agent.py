import asyncio
import os
import sys
from typing import List, Dict, Any
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from mcp.shared.exceptions import McpError
from litellm import acompletion
from dotenv import load_dotenv

load_dotenv()

class HRAgent:
    def __init__(self):
        self.server_params = StdioServerParameters(
            command=sys.executable,
            args=["mcp_server.py"]
        )
        self.session = None
        self.exit_stack = None

    async def connect(self):
        from contextlib import AsyncExitStack
        self.exit_stack = AsyncExitStack()
        
        transport = await self.exit_stack.enter_async_context(
            stdio_client(self.server_params)
        )
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(*transport)
        )
        await self.session.initialize()

    async def disconnect(self):
        if self.exit_stack:
            await self.exit_stack.aclose()
            
    async def get_tools(self) -> List[Dict[str, Any]]:
        tools_response = await self.session.list_tools()
        formatted_tools = []
        for tool in tools_response.tools:
            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
        return formatted_tools

    async def call_tool(self, name: str, arguments: dict) -> str:
        try:
            result = await self.session.call_tool(name, arguments)
            if not result.content:
                return "Tool returned empty result."
            
            # Combine content blocks
            return "\n".join(
                block.text if block.type == "text" else str(block) 
                for block in result.content
            )
        except McpError as e:
            return f"Error executing tool {name}: {str(e)}"
        except Exception as e:
            return f"Unexpected error executing tool {name}: {str(e)}"

    async def chat(self, user_message: str, history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a multi-step ReAct/Tool-calling loop using LiteLLM.
        """
        if not self.session:
            await self.connect()

        tools = await self.get_tools()
        
        messages = [{"role": "system", "content": "You are a helpful HR Assistant. You have tools to check policies (RAG) and look up employee data. Do not execute state-modifying actions without explicit user confirmation if it has real impact, but since this is mock data, you can proceed if requested. Always cite your sources when explaining policies."}]
        
        if history:
            messages.extend(history)
            
        messages.append({"role": "user", "content": user_message})
        
        trace = []
        
        while True:
            # Call LLM
            response = await acompletion(
                model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.2,
                api_key=os.getenv("GEMINI_API_KEY", os.getenv("LLM_API_KEY", "dummy")),
                base_url=os.getenv("LLM_BASE_URL", None)
            )
            
            message = response.choices[0].message
            messages.append(message)
            
            if not message.tool_calls:
                # Agent is done
                return {
                    "response": message.content,
                    "trace": trace
                }
                
            # Process tool calls
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                import json
                tool_args = json.loads(tool_call.function.arguments)
                
                trace.append({"tool": tool_name, "args": tool_args})
                
                tool_result = await self.call_tool(tool_name, tool_args)
                trace[-1]["result"] = tool_result
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": tool_result
                })
