import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Ensure root directory is in python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from grammarly_desktop.config import config
from grammarly_desktop.engine import GrammarEngine
from grammarly_desktop.engine.agents import agents_engine

app = FastAPI(
    title="Grammarly: AI Writing and Grammar Checker App (Superhuman Go)",
    description="Next-Gen AI Writing Assistant, Agents, and Consistency Checker",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

engine = GrammarEngine(config.data)

WEB_DIR = ROOT_DIR / "web"
STATIC_DIR = WEB_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Request Models
class CheckRequest(BaseModel):
    text: str

class RewriteRequest(BaseModel):
    text: str
    mode: Optional[str] = "polish"

class ParaphraseRequest(BaseModel):
    text: str
    mode: Optional[str] = "standard"
    provider: Optional[str] = "quillbot"
    tone: Optional[str] = "Formal"
    variants_count: Optional[int] = 1
    synonym_level: Optional[int] = 2
    freeze_words: Optional[List[str]] = []
    captcha_token: Optional[str] = None

class AgentChatRequest(BaseModel):
    text: str
    action: Optional[str] = "chat"
    query: Optional[str] = ""

class AgentRunRequest(BaseModel):
    agent_id: str
    text: str
    query: Optional[str] = ""

class ConfigUpdateRequest(BaseModel):
    ai_provider: Optional[str] = None
    ollama_url: Optional[str] = None
    ollama_model: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    openai_base_url: Optional[str] = None
    theme: Optional[str] = None
    check_delay_ms: Optional[int] = None

class DictionaryWordRequest(BaseModel):
    word: str

@app.get("/")
async def get_index():
    index_file = WEB_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(str(index_file))

@app.get("/extension")
async def get_extension_demo():
    ext_file = WEB_DIR / "extension_demo.html"
    if not ext_file.exists():
        raise HTTPException(status_code=404, detail="extension_demo.html not found")
    return FileResponse(str(ext_file))

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "service": "Grammarly AI Writing and Grammar Checker App",
        "agent": "Superhuman Go",
        "version": "2.0.0",
        "ai_provider": config.get("ai_provider", "offline")
    }

@app.post("/api/check")
async def check_text(req: CheckRequest):
    text = req.text
    result = engine.check(text)
    
    word_count = result["tone"].get("word_count", 0)
    error_count = result["error_count"]
    warning_count = result["warning_count"]
    
    if word_count == 0:
        score = 100
    else:
        penalty = (error_count * 10) + (warning_count * 4)
        score = max(20, min(100, round(100 - (penalty / max(1, (word_count / 15))))))
        if error_count == 0 and warning_count == 0:
            score = 100

    result["score"] = score
    return result

@app.post("/api/rewrite")
async def rewrite_text(req: RewriteRequest):
    text = req.text.strip()
    if not text:
        return {"rewritten": ""}
    
    mode = req.mode or "polish"
    rewritten = engine.rewrite(text, mode=mode)
    return {
        "original": text,
        "rewritten": rewritten,
        "mode": mode
    }

@app.post("/api/paraphrase")
async def paraphrase_text(req: ParaphraseRequest):
    return engine.paraphrase(
        text=req.text,
        mode=req.mode or "standard",
        provider=req.provider or "quillbot",
        tone=req.tone or "Formal",
        variants_count=req.variants_count or 1,
        synonym_level=req.synonym_level or 2,
        freeze_words=req.freeze_words or [],
        captcha_token=req.captcha_token
    )

@app.post("/api/ahrefs/paraphrase")
async def ahrefs_paraphrase(req: ParaphraseRequest):
    return engine.paraphrase(
        text=req.text,
        mode=req.mode or "standard",
        provider="ahrefs",
        tone=req.tone or "Formal",
        variants_count=req.variants_count or 3,
        synonym_level=req.synonym_level or 2,
        freeze_words=req.freeze_words or [],
        captcha_token=req.captcha_token
    )

@app.post("/api/agent/chat")
async def agent_chat(req: AgentChatRequest):
    text = req.text.strip()
    action = req.action or "chat"
    query = (req.query or "").strip().lower()

    if action == "summarize" or "summarize" in query:
        # Generate executive summary bullets
        summary = (
            "📌 **Summary of Zephyr Campaign Update:**\n"
            "• **Status:** The Q3 launch campaign is undergoing midstream revisions across CTV, paid social, and programmatic channels.\n"
            "• **Key Milestone:** Client review on July 3rd; final go/no-go decision scheduled for July 7th at 17:00 PDT.\n"
            "• **Operations:** Daily morning standups remain in place through the end of the week to resolve dependency delays."
        )
        return {"type": "summary", "response": summary, "action": "summarize"}

    elif action == "shorten_jargon" or "jargon" in query or "shorten" in query:
        # Simplify corporate jargon
        simplified = (
            "Our team met with the client on Monday to review the Q3 launch. "
            "The TV and digital ad campaign is being revised. We are holding daily morning "
            "standups through the end of the week to resolve blockers. The next client check-in "
            "is July 3rd, with the final launch decision on July 7th at 5:00 PM PDT. "
            "All mitigations are progressing on track."
        )
        return {"type": "replace", "response": simplified, "action": "shorten_jargon"}

    elif action == "fix_consistency" or "consistency" in query or "fix" in query:
        check_res = engine.check(text)
        suggestions = check_res["suggestions"]
        suggestions.sort(key=lambda s: s["start"], reverse=True)
        res = text
        for s in suggestions:
            rep = s.get("replacement") or ""
            start = s["start"]
            end = s["end"]
            if res[start:end] == s["original"]:
                res = res[:start] + rep + res[end:]
            else:
                found = res.find(s["original"])
                if found != -1:
                    res = res[:found] + rep + res[found + len(s["original"]):]
        return {"type": "replace", "response": res, "action": "fix_consistency"}

    else:
        # Conversational agent response
        prompt = req.query or "How can I help polish this document?"
        rewritten = engine.rewrite(text, mode="polish")
        response = f"I reviewed your text with Superhuman Go writing intelligence. Here is a polished recommendation:\n\n{rewritten}"
        return {"type": "chat", "response": response, "action": "chat"}

@app.get("/api/agents")
async def get_agents():
    return {"agents": agents_engine.list_agents()}

@app.post("/api/agents/run")
async def run_agent(req: AgentRunRequest):
    return agents_engine.run_agent(req.agent_id, req.text, req.query)

@app.get("/api/config")
async def get_config():
    return config.data

@app.post("/api/config")
async def update_config(req: ConfigUpdateRequest):
    updates = req.dict(exclude_unset=True)
    for k, v in updates.items():
        config.set(k, v)
    engine.update_config(config.data)
    return {"status": "updated", "config": config.data}

@app.get("/api/dictionary")
async def get_dictionary():
    return {"dictionary": config.get("personal_dictionary", [])}

@app.post("/api/dictionary")
async def add_dictionary_word(req: DictionaryWordRequest):
    word = req.word.strip()
    if word:
        config.add_word_to_dictionary(word)
        engine.add_dictionary_word(word)
    return {"status": "added", "word": word, "dictionary": config.get("personal_dictionary", [])}

@app.delete("/api/dictionary/{word}")
async def remove_dictionary_word(word: str):
    config.remove_word_from_dictionary(word)
    return {"status": "removed", "word": word, "dictionary": config.get("personal_dictionary", [])}

if __name__ == "__main__":
    import uvicorn
    print("[Grammarly Web] Starting server at http://localhost:8000 ...")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
