import os
import json
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# =====================================================
# CONFIGURATION
# =====================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

SPI_DATA_URL = "https://projects.fivethirtyeight.com/soccer-api/club/spi_matches.csv"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

app = FastAPI(title="DSN AI Match Prediction API")

# =====================================================
# CORS (ALLOW ALL DOMAINS)
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# ROOT ROUTE
# =====================================================
@app.get("/")
def root():
    return {
        "message": "DSN AI Match Prediction API is running",
        "endpoints": ["/predict", "/health", "/docs"]
    }

# =====================================================
# HEALTH CHECK
# =====================================================
@app.get("/health")
def health():
    return {"status": "ok", "message": "Application running successfully"}

# =====================================================
# REQUEST MODEL (POST)
# =====================================================
class MatchRequest(BaseModel):
    team_a: str
    team_b: str

# =====================================================
# LOAD REAL CURRENT DATA
# =====================================================
def load_spi_data():
    try:
        return pd.read_csv(SPI_DATA_URL)
    except Exception as e:
        raise RuntimeError(f"Failed to load SPI data: {e}")

# =====================================================
# TEAM STATISTICS
# =====================================================
def get_team_stats(df, team_name):
    matches = df[
        (df["team1"] == team_name) | (df["team2"] == team_name)
    ].sort_values("date", ascending=False).head(5)

    if matches.empty:
        return None

    goals_for, goals_against, wins = 0, 0, 0

    for _, row in matches.iterrows():
        if row["team1"] == team_name:
            goals_for += row["score1"]
            goals_against += row["score2"]
            if row["score1"] > row["score2"]:
                wins += 1
            spi = row["spi1"]
        else:
            goals_for += row["score2"]
            goals_against += row["score1"]
            if row["score2"] > row["score1"]:
                wins += 1
            spi = row["spi2"]

    return {
        "matches_analyzed": len(matches),
        "wins_last_5": wins,
        "goals_scored": goals_for,
        "goals_conceded": goals_against,
        "spi_rating": round(float(spi), 2)
    }

# =====================================================
# OPENAI HTTP REQUEST
# =====================================================
def openai_prediction(team_a, team_b, stats_a, stats_b):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a professional football analyst.

Use ONLY the provided data.

Team A: {team_a}
Stats: {stats_a}

Team B: {team_b}
Stats: {stats_b}

Tasks:
- Predict the winner
- Provide win probabilities
- Explain clearly why one team may win or lose
- Mention form, attack, defense, and SPI rating

Return valid JSON only:
{{
  "winner": "",
  "team_a_probability": "",
  "team_b_probability": "",
  "analysis": ""
}}
"""

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You analyze football matches using statistical data only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.35
    }

    try:
        response = requests.post(
            OPENAI_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"OpenAI API request failed: {e}")
    except (KeyError, json.JSONDecodeError):
        raise RuntimeError("Unexpected OpenAI response format")

# =====================================================
# POST /predict (PRODUCTION)
# =====================================================
@app.post("/predict")
def predict_post(request: MatchRequest):
    df = load_spi_data()

    stats_a = get_team_stats(df, request.team_a)
    stats_b = get_team_stats(df, request.team_b)

    if not stats_a or not stats_b:
        raise HTTPException(status_code=404, detail="One or both teams not found")

    prediction = openai_prediction(
        request.team_a, request.team_b, stats_a, stats_b
    )

    return {
        "team_a": request.team_a,
        "team_b": request.team_b,
        "prediction": prediction
    }

# =====================================================
# GET /predict (BROWSER TESTING)
# =====================================================
@app.get("/predict")
def predict_get(team_a: str, team_b: str):
    df = load_spi_data()

    stats_a = get_team_stats(df, team_a)
    stats_b = get_team_stats(df, team_b)

    if not stats_a or not stats_b:
        return {"error": "One or both teams not found"}

    prediction = openai_prediction(team_a, team_b, stats_a, stats_b)

    return {
        "team_a": team_a,
        "team_b": team_b,
        "prediction": prediction
    }

# =====================================================
# STARTUP LOG
# =====================================================
print("SUCCESS: DSN API started correctly")        "wins_last_5": wins,
        "goals_scored": goals_for,
        "goals_conceded": goals_against,
        "spi_rating": round(float(spi), 2)
    }

# =====================================================
# OPENAI HTTP REQUEST
# =====================================================
def openai_prediction(team_a, team_b, stats_a, stats_b):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a professional football analyst.

Use ONLY the provided data.

Team A: {team_a}
Stats: {stats_a}

Team B: {team_b}
Stats: {stats_b}

Tasks:
- Predict the winner
- Provide win probabilities
- Explain clearly why one team may win or lose
- Mention form, attack, defense, and SPI rating

Return valid JSON only:
{{
  "winner": "",
  "team_a_probability": "",
  "team_b_probability": "",
  "analysis": ""
}}
"""

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You analyze football matches using statistical data only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.35
    }

    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        # Ensure valid JSON
        return json.loads(content)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"OpenAI API request failed: {e}")
    except (KeyError, json.JSONDecodeError):
        raise RuntimeError(f"Unexpected OpenAI response format: {result}")

# =====================================================
# API ENDPOINTS
# =====================================================

# POST endpoint for production frontend
@app.post("/predict")
def predict_post(request: MatchRequest):
    team_a = request.team_a
    team_b = request.team_b
    df = load_spi_data()

    stats_a = get_team_stats(df, team_a)
    stats_b = get_team_stats(df, team_b)

    if not stats_a or not stats_b:
        raise HTTPException(status_code=404, detail="One or both teams not found in dataset")

    prediction = openai_prediction(team_a, team_b, stats_a, stats_b)
    return {"team_a": team_a, "team_b": team_b, "prediction": prediction}

# GET endpoint for quick testing in browser
@app.get("/predict")
def predict_get(team_a: str, team_b: str):
    df = load_spi_data()

    stats_a = get_team_stats(df, team_a)
    stats_b = get_team_stats(df, team_b)

    if not stats_a or not stats_b:
        return {"error": "One or both teams not found in dataset"}

    prediction = openai_prediction(team_a, team_b, stats_a, stats_b)
    return {"team_a": team_a, "team_b": team_b, "prediction": prediction}

# Health check route
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Application running successfully"}

# =====================================================
# STARTUP CHECK
# =====================================================
print("SUCCESS: Application started correctly")
