# Filename: app.py
# Requirements: fastapi, requests, python-dotenv, uvicorn
# Install with: pip install fastapi requests python-dotenv uvicorn

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

app = FastAPI(title="Match Prediction AI Engine")

# ----------------------
# Environment Variables
# ----------------------
# HUGGINGFACE_API_KEY is your Hugging Face API key
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
if not HF_API_KEY:
    raise Exception("Please set your HUGGINGFACE_API_KEY in .env file")

# SportSRC feed URL (example: football matches)
SPORTSRC_URL = "https://api.sportsrc.org/?data=matches&category=football"  

# Hugging Face Model
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

# ----------------------
# Request Body Model
# ----------------------
class PredictionRequest(BaseModel):
    home_team: str
    away_team: str

# ----------------------
# Helper Functions
# ----------------------
def fetch_current_matches():
    """Fetch live matches JSON from SportSRC feed"""
    try:
        response = requests.get(SPORTSRC_URL)
        response.raise_for_status()
        data = response.json()
        return data  # raw JSON data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def find_match_data(home_team, away_team, matches):
    """Find specific match by team names"""
    for match in matches:
        ht = match.get("home_team", "").lower()
        at = match.get("away_team", "").lower()
        if ht == home_team.lower() and at == away_team.lower():
            return match
    return None

def build_prompt(match_data):
    """Build a prompt for AI to reason about winner"""
    if not match_data:
        return "No match data available for the selected teams."
    
    prompt = f"""
You are a sports analyst AI. Given the following match data, predict which team is more likely to win and explain why:

Home Team: {match_data.get('home_team')}
Away Team: {match_data.get('away_team')}
Home Form (last 5 matches): {match_data.get('home_form', 'N/A')}
Away Form (last 5 matches): {match_data.get('away_form', 'N/A')}
Head-to-Head: {match_data.get('head_to_head', 'N/A')}
Injuries: {match_data.get('injuries', 'N/A')}
Home Advantage: {match_data.get('home_advantage', 'N/A')}
Other Stats: {match_data.get('other_stats', 'N/A')}

Provide your prediction clearly, reasoning, and probability estimate for each outcome (Home win, Draw, Away win).
"""
    return prompt

def query_huggingface(prompt):
    """Call Hugging Face Inference API with Mistral 7B Instruct"""
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.7,
            "return_full_text": True
        }
    }

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {response.text}")
    
    result = response.json()
    # Hugging Face returns a list with 'generated_text'
    return result[0]["generated_text"] if isinstance(result, list) else str(result)

# ----------------------
# API Endpoint
# ----------------------
@app.post("/predict")
def predict_winner(request: PredictionRequest):
    # Step 1: Fetch live matches
    matches = fetch_current_matches()
    if not matches:
        raise HTTPException(status_code=500, detail="Failed to fetch live match data")
    
    # Step 2: Find requested match
    match_data = find_match_data(request.home_team, request.away_team, matches)
    if not match_data:
        raise HTTPException(status_code=404, detail="Match not found in current data")
    
    # Step 3: Build AI prompt
    prompt = build_prompt(match_data)
    
    # Step 4: Query Hugging Face model
    prediction = query_huggingface(prompt)
    
    # Step 5: Return result
    return {"prediction": prediction}

# ----------------------
# Run locally: uvicorn app:app --reload
# On Render: it will auto-detect FastAPI
# ----------------------
