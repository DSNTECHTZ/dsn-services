import pandas as pd
import requests
from fastapi import FastAPI
from openai import OpenAI
import os

# -----------------------------
# CONFIG
# -----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SPI_DATA_URL = "https://projects.fivethirtyeight.com/soccer-api/club/spi_matches.csv"

client = OpenAI(api_key=OPENAI_API_KEY)
app = FastAPI(title="AI Match Prediction Bot")

# -----------------------------
# LOAD REAL CURRENT DATA
# -----------------------------
def load_spi_data():
    df = pd.read_csv(SPI_DATA_URL)
    return df

# -----------------------------
# EXTRACT TEAM STATS
# -----------------------------
def get_team_form(df, team_name):
    team_matches = df[
        (df["team1"] == team_name) | (df["team2"] == team_name)
    ].sort_values("date", ascending=False).head(5)

    if team_matches.empty:
        return None

    goals_for = 0
    goals_against = 0
    wins = 0

    for _, row in team_matches.iterrows():
        if row["team1"] == team_name:
            goals_for += row["score1"]
            goals_against += row["score2"]
            if row["score1"] > row["score2"]:
                wins += 1
        else:
            goals_for += row["score2"]
            goals_against += row["score1"]
            if row["score2"] > row["score1"]:
                wins += 1

    spi_rating = team_matches.iloc[0]["spi1"] if team_matches.iloc[0]["team1"] == team_name else team_matches.iloc[0]["spi2"]

    return {
        "recent_matches": len(team_matches),
        "wins_last_5": wins,
        "goals_scored": goals_for,
        "goals_conceded": goals_against,
        "spi_rating": spi_rating
    }

# -----------------------------
# OPENAI ANALYSIS
# -----------------------------
def ai_predict(team_a, team_b, stats_a, stats_b):
    prompt = f"""
You are a professional football match analyst.

Use ONLY the data provided below.

Team A: {team_a}
Stats: {stats_a}

Team B: {team_b}
Stats: {stats_b}

Tasks:
1. Predict the most likely winner
2. Give win probabilities for both teams
3. Explain clearly why one team is likely to win or lose
4. Mention form, attack, defense, and SPI rating

Respond in JSON format:
{{
  "winner": "",
  "team_a_win_probability": "",
  "team_b_win_probability": "",
  "analysis": ""
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You analyze football matches using statistical data."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.35
    )

    return response.choices[0].message.content

# -----------------------------
# API ENDPOINT
# -----------------------------
@app.post("/predict")
def predict(team_a: str, team_b: str):
    df = load_spi_data()

    stats_a = get_team_form(df, team_a)
    stats_b = get_team_form(df, team_b)

    if not stats_a or not stats_b:
        return {
            "error": "One or both teams not found in current dataset."
        }

    prediction = ai_predict(team_a, team_b, stats_a, stats_b)

    return {
        "team_a": team_a,
        "team_b": team_b,
        "prediction": prediction
    }        "prediction": output_text,
        "match": match
    }
