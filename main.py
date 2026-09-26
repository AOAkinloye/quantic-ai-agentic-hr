import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from contextlib import asynccontextmanager
from agent import HRAgent

hr_agent = HRAgent()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await hr_agent.connect()
    yield
    await hr_agent.disconnect()

app = FastAPI(title="HR Agent API", lifespan=lifespan)

templates = Jinja2Templates(directory="templates")

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, Any]]] = []

class ChatResponse(BaseModel):
    response: str
    trace: List[Dict[str, Any]]

@app.get("/health")
async def health_check():
    mcp_status = "connected" if hr_agent.session else "disconnected"
    return {"status": "ok", "mcp_connection": mcp_status}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        result = await hr_agent.chat(request.message, request.history)
        return ChatResponse(
            response=result["response"],
            trace=result["trace"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="index.html"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
