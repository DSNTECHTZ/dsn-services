from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# DeepSeek client (compatible with OpenAI SDK)
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

SYSTEM_PROMPT = """
You are DSN ASSISTANT, a professional customer support AI
for DSN TECHNOLOGY only.

RULES:
- Ongea Kiswahili kama lugha kuu, English kidogo pale inapohitajika
- Elezea huduma za DSN TECHNOLOGY TU (hakuna mada nyingine)
- Toa majibu mafupi, sahihi, na ya kibiashara
- Kama mteja anahitaji msaada zaidi, mpe WhatsApp: 0745720609
- Usijibu maswali yasiyo husu DSN TECHNOLOGY

DSN TECHNOLOGY SERVICES:
1. Website Design (kuanzia Tsh 49,000)
2. Mobile App Development
3. Logo Design (2D & 3D)
4. AI Bots & Automation
5. Video Editing
6. Tech Support & Consultation

BUSINESS CONTACT:
WhatsApp: 0745720609
"""

@app.route("/", methods=["GET"])
def home():
    return "DSN ASSISTANT is running successfully 🚀"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            stream=False
        )

        reply = response.choices[0].message.content

        # Kama bot inaona mteja anahitaji msaada zaidi
        if "contact" in user_message.lower() or "whatsapp" in user_message.lower():
            reply += "\n\n📞 WhatsApp Support: 0745720609"

        return jsonify({
            "success": True,
            "bot": "DSN ASSISTANT",
            "reply": reply
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
