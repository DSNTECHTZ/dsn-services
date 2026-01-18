from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)  # 👈 HII NDIO FIX KUU

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

SYSTEM_PROMPT = """
You are DSN ASSISTANT, a professional customer support AI
for DSN TECHNOLOGY only.

- Lugha kuu: Kiswahili, English kidogo
- Huduma za DSN TECHNOLOGY tu
- Toa bei na msaada
- WhatsApp: 0745720609
"""

@app.route("/", methods=["GET"])
def home():
    return "DSN ASSISTANT is running successfully 🚀"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    return jsonify({
        "success": True,
        "reply": response.choices[0].message.content
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)    app.run(host="0.0.0.0", port=10000)
