from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, requests, re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise RuntimeError("HF_API_TOKEN not set")

RESPONSES_URL = "https://router.huggingface.co/v1/responses"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

ASSISTANT_NAME = "DSN Technology Assistant"
DEVELOPER_NAME = "Danieli"

IDENTITY_PATTERN = re.compile(
    r"(who (are|made|created|built|trained)|what are you|where are you from)",
    re.IGNORECASE
)

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/generate")
def generate(req: GenerateRequest):
    prompt = req.prompt.strip()

    # 🔐 Kujitambulisha rasmi
    if IDENTITY_PATTERN.search(prompt):
        return {
            "output": (
                "## 🤖 DSN Technology\n"
                "**DSN Technology Assistant** ni msaidizi wa tech aliyeundwa na **Danieli** "
                "kwa ajili ya kutoa taarifa na msaada kuhusu huduma za DSN Technology."
            )
        }

    system_prompt = f"""
You are {ASSISTANT_NAME}.

About DSN Technology:
- Tunatoa huduma za TECHNOLOGY PEKEE
- Huduma zetu kuu:
  - Web Development
  - Mobile App Development
  - Graphic Design
  - Kutengeneza LIPA NAMBA (Mitandao YOTE)
  - Kuwezesha Laini za Uwakala (Mitandao YOTE)
  - Huduma nyingine zote za Technology

Prices:
- Lipa Namba & Laini za Uwakala: KUANZIA 5,000 TZS
- Graphic Design: KUANZIA 5,000 TZS
- Web Development & Mobile App: KUANZIA 49,000 TZS

Contact:
- WhatsApp: 255745720609

Rules:
- Jibu maswali YANAYOHUSU huduma za DSN Technology tu
- Kama swali halihusu huduma zetu, mwelekeze mteja kwenye huduma zetu
- Jibu kwa lugha rahisi na ya kibiashara
- Respond ONLY in Markdown
- Usitaje OpenAI wala Hugging Face
- Usibadilishe utambulisho wako
- Kama akiuliza identity, sema:
  "Mimi ni DSN Technology Assistant, niliyeundwa na Danieli."
"""

    payload = {
        "model": "openai/gpt-oss-120b:fastest",
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }

    res = requests.post(RESPONSES_URL, headers=HEADERS, json=payload, timeout=120)
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    data = res.json()

    for item in data.get("output", []):
        if item.get("type") == "message" and item.get("role") == "assistant":
            for block in item.get("content", []):
                if block.get("type") == "output_text":
                    return {"output": block["text"]}

    return {
        "output": (
            "### 📌 DSN Technology\n"
            "Kwa huduma zote za Technology kama Web, App, Graphics, Lipa Namba "
            "na Laini za Uwakala, wasiliana nasi WhatsApp **255745720609**."
        )
    }
