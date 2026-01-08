import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

SPORTDB_KEY = os.getenv("SPORTDB_API_KEY")
HF_KEY = os.getenv("HF_API_KEY")

assert SPORTDB_KEY, "SPORTDB_API_KEY missing"
assert HF_KEY, "HF_API_KEY missing"

# --------- Request Body ---------
class PredictRequest(BaseModel):
    teamA: str
    teamB: str
    competition: str = ""


# --------- Fetch Live Data from SportDB.dev ---------
def fetch_live_match(teamA: str, teamB: str):
    base_url = "https://sportdb.dev/api/football/live"
    headers = {"X-API-KEY": SPORTDB_KEY}
    resp = requests.get(base_url, headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Error fetching match data")
    data = resp.json()

    # Find a match that includes the given teams
    for m in data.get("data", []):
        h = m.get("home_team", "").lower()
        a = m.get("away_team", "").lower()
        if teamA.lower() in h and teamB.lower() in a:
            return m
    return None


# --------- Build Prompt ---------
def build_prompt(match_data: dict):
    home = match_data.get("home_team")
    away = match_data.get("away_team")
    stats = match_data.get("stats", {})

    # Build simple text block for AI prompt
    prompt = (
        f"Given the match between {home} and {away}:\n"
        f"Score: {match_data.get('score', 'N/A')}\n"
        f"Match status: {match_data.get('status', 'unknown')}\n"
        f"Stats available: {stats}\n\n"
        "Based on this information, predict who "
        "is more likely to win and explain why in detail."
    )
    return prompt


# --------- Call Hugging Face Inference API ---------
def call_hf(prompt: str):
    HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

    headers = {
        "Authorization": f"Bearer {HF_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": f"<s>[INST] {prompt} [/INST]",
        "parameters": {
            "max_new_tokens": 256,
            "temperature": 0.7
        }
    }

    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Hugging Face error: {resp.text}"
        )
    return resp.json()


# --------- API Endpoint ---------
@app.post("/predict")
def predict(req: PredictRequest):
    match = fetch_live_match(req.teamA, req.teamB)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found or not live")

    prompt = build_prompt(match)
    hf_resp = call_hf(prompt)

    # HF returns list or dict depending on model output
    output_text = ""
    if isinstance(hf_resp, list) and len(hf_resp) > 0:
        output_text = hf_resp[0].get("generated_text", "")
    elif isinstance(hf_resp, dict) and "generated_text" in hf_resp:
        output_text = hf_resp.get("generated_text", "")
    else:
        output_text = str(hf_resp)

    return {
        "prediction": output_text,
        "match": match
    }
