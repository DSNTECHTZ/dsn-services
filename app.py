import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# --- CONFIGURATION ---
# Tunachukua API KEY kutoka kwa Render Environment Variables kwa usalama
api_key = os.environ.get("DEEPSEEK_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# --- SYSTEM PROMPT (AKILI YA BOT) ---
# Hapa ndipo tunapomfundisha bot kuwa DSN Assistant na si vinginevyo.
SYSTEM_INSTRUCTION = """
Wewe ni 'DSN Assistant', mtoa huduma msaidizi (customer support) wa kampuni inayoitwa DSN Technology.

MAAGIZO YA KAZI YAKO:
1. Lugha Kuu: Kiswahili na English.
2. Jibu maswali yanayohusu huduma, bei, na bidhaa za DSN Technology TU.
3. Usijibu maswali ya siasa, mapishi, michezo, au kampuni nyingine yoyote.
4. Ukiona mteja anauliza kitu kisichohusu DSN, sema kwa heshima: "Samahani, mimi ni msaidizi wa DSN Technology pekee. Naweza kukusaidia na huduma zetu."
5. Ukiona huelewi swali, au mteja anahitaji msaada wa kina ambao huwezi kutatua, mpe namba hii ya WhatsApp: 0745720609.
6. Kuwa rafiki, professional, na mfupi kwenye maelezo isipokuwa ukiulizwa ufafanuzi.

MUKTADHA WA DSN TECHNOLOGY (Tumia hizi data kujibu):
- Kampuni: DSN Technology.
- Mawasiliano: 0745720609 (WhatsApp/Call).
- Huduma zetu: (Weka orodha ya huduma zako hapa, mfano: Kutengeneza Website, Graphics Design, System Development, n.k - Jaza unavyotaka).
"""

@app.route('/')
def home():
    return "DSN Assistant Bot is Running!"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Tuma maombi kwa DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": user_message},
            ],
            stream=False,
            temperature=0.7 # 0.7 inafanya majibu yawe ya ubunifu kidogo lakini sahihi
        )

        bot_reply = response.choices[0].message.content
        return jsonify({"reply": bot_reply})

    except Exception as e:
        # Ikitokea error yoyote, tunarudisha ujumbe huu
        return jsonify({"reply": "Samahani, kuna tatizo la kiufundi. Tafadhali wasiliana nasi WhatsApp 0745720609."}), 500

if __name__ == '__main__':
    # Hii inatumika local tu, Render itatumia Gunicorn
    app.run(debug=True)
