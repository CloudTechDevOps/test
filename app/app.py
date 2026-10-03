"""AI agent served with Ray Serve on KubeRay, powered by Google Gemini."""
import logging
import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from ray import serve

from chat import MAX_HISTORY, build_contents

log = logging.getLogger("ray.serve")

MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
SYSTEM_PROMPT = "You are a helpful assistant. Be concise."
INDEX_HTML = Path(__file__).parent / "static" / "index.html"

api = FastAPI(title="KubeRay Gemini Agent")


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    history: list[Message] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    model: str


@serve.deployment(
    autoscaling_config={"min_replicas": 1, "max_replicas": 3, "target_ongoing_requests": 5},
    ray_actor_options={"num_cpus": 0.25},
)
@serve.ingress(api)
class Agent:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        self.client = genai.Client(api_key=api_key)
        self.config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
            max_output_tokens=1024,
        )
        self.index_html = INDEX_HTML.read_text(encoding="utf-8")

    @api.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index(self):
        return HTMLResponse(self.index_html)

    @api.get("/healthz")
    def health(self):
        return {"status": "ok", "model": MODEL_ID}

    @api.post("/chat", response_model=ChatResponse)
    def chat(self, req: ChatRequest):
        if len(req.history) > MAX_HISTORY * 2:
            raise HTTPException(status_code=422, detail="history too long")
        history = [{"role": m.role, "content": m.content} for m in req.history]
        contents = build_contents(history, req.message)
        try:
            resp = self.client.models.generate_content(
                model=MODEL_ID, contents=contents, config=self.config
            )
        except Exception:
            log.exception("gemini call failed")
            raise HTTPException(status_code=502, detail="model call failed")
        return ChatResponse(answer=resp.text or "", model=MODEL_ID)


app = Agent.bind()
