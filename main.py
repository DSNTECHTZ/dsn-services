from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, requests, re

app = FastAPI(title="DSN Technology API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Hugging Face (OPTIONAL)
# Kama hutaki kutumia HF kabisa, utaondoa sehemu hii
# =========================
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
RESPONSES_URL = "https://router.huggingface.co/v1/responses"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

# =========================
# DSN Technology Identity
# =========================
ASSISTANT_NAME = "DSN Technology Assistant"
DEVELOPER_NAME = "Danieli Emanueli"
COMPANY_NAME = "DSN Technology"

WHATSAPP_NUMBER = "255745720609"

SERVICES_INFO = """
### 🚀 DSN Technology Services

Tunatoa huduma zote za Teknolojia ikiwemo:

#### 💻 Web Development
- Website za biashara, blog, kampuni
- Bei kuanzia **49,000 TZS**

#### 📱 App Development
- Android Apps
- App za biashara na huduma
- Bei kuanzia **49,000 TZS**

#### 🎨 Graphics Design
- Logo
- Posters
- Banners
- Social media designs
- Bei kuanzia **5,000 TZS**

#### 💰 LIPA Numbers (Mitandao YOTE)
- LIPA Namba zote (M-Pesa, Tigo Pesa, Airtel Money, HaloPesa n.k)
- Pia laini za uwakala
- Bei kuanzia **5,000 TZS**

#### 🛠 Huduma Nyingine za Tech
- API integration
- Payment systems
- System setup
- Tech support na ushauri

📞 **Wasiliana nasi WhatsApp:** **{WHATSAPP_NUMBER}**
"""

IDENTITY_PATTERN = re.compile(
    r"(wewe ni nani|nani alikutengeneza|nani developer|uliumbwa na nani|who are you|who made you)",
    re.IGNORECASE
)

OUT_OF_SCOPE_PATTERN = re.compile(
    r"(siasa|mapenzi|muziki|movie|dini|betting|prediction)",
    re.IGNORECASE
)

class GenerateRequest(BaseModel):
    prompt: str


@app.post("/generate")
def generate(req: GenerateRequest):
    prompt = req.prompt.strip()

    # 🔒 Identity response
    if IDENTITY_PATTERN.search(prompt):
        return {
            "output": (
                f"## 🤖 {ASSISTANT_NAME}\n"
                f"Mimi ni **DSN Technology Assistant**, niliyetengenezwa na **{DEVELOPER_NAME}**.\n\n"
                f"Tunatoa huduma za Teknolojia pekee."
            )
        }

    # 🚫 Maswali nje ya huduma zetu
    if OUT_OF_SCOPE_PATTERN.search(prompt):
        return {
            "output": (
                "### ❌ Huduma Hiyo Hatuitoi\n"
                "DSN Technology tunajikita kwenye **huduma za Teknolojia pekee** kama web, app, graphics na malipo.\n\n"
                f"📲 Wasiliana nasi WhatsApp: **{WHATSAPP_NUMBER}**"
            )
        }

    # ✅ Majibu ya huduma zetu
    # Kama hutaki kutumia Hugging Face, response hii inatosha
    return {
        "output": SERVICES_INFO.format(WHATSAPP_NUMBER=WHATSAPP_NUMBER)
    }


@app.get("/")
def root():
    return {
        "service": "DSN Technology API",
        "developer": DEVELOPER_NAME,
        "contact": WHATSAPP_NUMBER
    }
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
