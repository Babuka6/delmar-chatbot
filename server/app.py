# server/app.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import List
import sys, html, os

# Load .env from project root for local dev; hosts will inject real env vars
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

print(">>> Running Python:", sys.version)

from schemas import CompleteRequest, AnswerRequest
from emailer import send_email
from llm import answer_user, format_summary

app = FastAPI()
CONTENT_SNIPPETS = ""  # optional

@app.get("/debug/send_test_email")
def send_test_email():
    try:
        send_email("SMTP sanity check", "<h1>It works</h1><p>Sent from FastAPI.</p>")
        return {"ok": True}
    except Exception as e:
        raise HTTPException(502, f"Email failed: {e}")

@app.post("/chat/answer")
def chat_answer(req: AnswerRequest):
    try:
        reply = answer_user(req.message, CONTENT_SNIPPETS)
    except Exception as e:
        raise HTTPException(500, f"LLM call failed: {e}")
    return JSONResponse({"answer": reply})

@app.post("/chat/complete")
def chat_complete(req: CompleteRequest):
    email = (req.answers.get("email") or "").strip()
    if "@" not in email:
        raise HTTPException(400, "Valid email required.")

    transcript_dicts: List[dict] = [m.model_dump() for m in req.transcript]
    subject, summary = format_summary(req.answers, transcript_dicts)
    body_html = "<pre style='font-family:ui-monospace, SFMono-Regular, Menlo, monospace; white-space:pre-wrap;'>" + html.escape(summary) + "</pre>"

    try:
        send_email(subject, body_html)
    except Exception as e:
        raise HTTPException(502, f"Email failed: {e}")

    return JSONResponse({"ok": True})

# Serve the project root (where index.html sits)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
app.mount("/", StaticFiles(directory=str(PROJECT_ROOT), html=True), name="site")
