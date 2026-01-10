import os
import json
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException

# =====================================================
# CONFIGURATION
# =====================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

SPI_DATA_URL = "https://projects.fivethirtyeight.com/soccer-api/club/spi_matches.csv"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

app = FastAPI(title="AI Football Match Prediction Bot")

# =====================================================
# LOAD REAL CURRENT DATA (NO API KEY REQUIRED)
# =====================================================

def load_spi_data():
    try:
        df = pd.read_csv(SPI_DATA_URL)
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to load SPI data: {e}")

# =====================================================
# TEAM STATISTICS EXTRACTION
# =====================================================

def get_team_stats(df, team_name):
    matches = df[
        (df["team1"] == team_name) | (df["team2"] == team_name)
    ].sort_values("date", ascending=False).head(5)

    if matches.empty:
        return None

    goals_for = 0
    goals_against = 0
    wins = 0

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
# OPENAI HTTP REQUEST (NO SDK HELPERS)
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
        result = response.json()
        return result["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"OpenAI API request failed: {e}")
    except KeyError:
        raise RuntimeError("Unexpected OpenAI response format")

# =====================================================
# API ENDPOINT
# =====================================================

@app.post("/predict")
def predict(team_a: str, team_b: str):
    try:
        df = load_spi_data()

        stats_a = get_team_stats(df, team_a)
        stats_b = get_team_stats(df, team_b)

        if not stats_a or not stats_b:
            raise HTTPException(
                status_code=404,
                detail="One or both teams not found in current dataset"
            )

        ai_result = openai_prediction(team_a, team_b, stats_a, stats_b)

        return {
            "team_a": team_a,
            "team_b": team_b,
            "prediction": json.loads(ai_result)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# STARTUP CHECK
# =====================================================

print("SUCCESS: Application started correctly")
