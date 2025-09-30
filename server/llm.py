# server/llm.py
import os
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_QA = """You are Del Mar Photonics' website assistant.
Answer in <=3 sentences. Do not promise prices or delivery times. If uncertain, ask 1 brief clarifying question.
Use supplied CONTEXT only as informal reference; do not invent details.
"""

SYSTEM_SUMMARY = """You draft email summaries for the business owner.
Produce:
1) A concise bullet summary of requirements (who, what, constraints, timeline).
2) A recommended next step (one short line).
3) A subject line (<=70 chars).
Be crisp and client-friendly.
"""

def answer_user(message: str, context_snippets: str = "") -> str:
    user = f"CONTEXT:\n{context_snippets}\n\nUSER:\n{message}"
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_QA},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()

def format_summary(answers, transcript) -> tuple[str, str]:
    t = "\n".join([f"{m['role']}: {m['text']}" for m in transcript])
    user = f"STRUCTURED ANSWERS:\n{answers}\n\nFULL TRANSCRIPT:\n{t}"
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_SUMMARY},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )
    out = resp.choices[0].message.content.strip()
    subject = "New website lead – summary"
    return subject, out
