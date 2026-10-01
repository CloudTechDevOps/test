"""AI agent served with Ray Serve on KubeRay, powered by Google Gemini."""
import logging
import os

from fastapi import FastAPI, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from ray import serve

from tools import TOOLS

log = logging.getLogger("ray.serve")

MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
SYSTEM_PROMPT = "You are a helpful assistant. Use tools when they help answer accurately. Be concise."

api = FastAPI(title="KubeRay Gemini Agent")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


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
            tools=TOOLS,  # SDK runs the tool-calling loop automatically
            temperature=0.2,
            max_output_tokens=1024,
        )

    @api.get("/healthz")
    def health(self):
        return {"status": "ok", "model": MODEL_ID}

    @api.post("/chat", response_model=ChatResponse)
    def chat(self, req: ChatRequest):
        try:
            resp = self.client.models.generate_content(
                model=MODEL_ID, contents=req.message, config=self.config
            )
        except Exception:
            log.exception("gemini call failed")
            raise HTTPException(status_code=502, detail="model call failed")
        return ChatResponse(answer=resp.text or "", model=MODEL_ID)


app = Agent.bind()
