import os
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify

# ==============================
# CONFIG
# ==============================
HF_MODEL = "gpt2-medium"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HF_TOKEN = os.getenv("HF_TOKEN")  # optional

HEADERS = {"Content-Type": "application/json"}
if HF_TOKEN:
    HEADERS["Authorization"] = f"Bearer {HF_TOKEN}"

# ==============================
# FLASK APP
# ==============================
app = Flask(__name__)

# ==============================
# AI CALL
# ==============================
def ask_ai(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 120,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
    }
    try:
        response = requests.post(HF_API_URL, headers=HEADERS, data=json.dumps(payload), timeout=60)
        response.raise_for_status()
        result = response.json()
        return result[0]["generated_text"]
    except Exception as e:
        return f"AI Error: {str(e)}"

# ==============================
# BUILD PROMPT
# ==============================
def build_prompt(match_data):
    return f"""
You are an AI football betting analyst.

Analyze the match and predict the winner.

MATCH DATE: {match_data['date']}
LEAGUE: {match_data['league']}

HOME TEAM: {match_data['home_team']}
AWAY TEAM: {match_data['away_team']}

HOME TEAM FORM (last 5): {match_data['home_form']}
AWAY TEAM FORM (last 5): {match_data['away_form']}

HOME GOALS AVG: {match_data['home_goals_avg']}
AWAY GOALS AVG: {match_data['away_goals_avg']}

HEAD TO HEAD: {match_data['h2h']}

TASK:
1. Predict winner (Home / Away / Draw)
2. Give short reasoning
3. Give confidence percentage
"""

# ==============================
# API ROUTE
# ==============================
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    required_fields = [
        "league",
        "home_team",
        "away_team",
        "home_form",
        "away_form",
        "home_goals_avg",
        "away_goals_avg",
        "h2h"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    match_data = {
        "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        **data
    }

    prompt = build_prompt(match_data)
    prediction = ask_ai(prompt)

    return jsonify({"status": "success", "prediction": prediction})

# ==============================
# HEALTH CHECK
# ==============================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "AI Betting Engine Running", "model": HF_MODEL})

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
