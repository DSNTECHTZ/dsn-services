import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)  # Inaruhusu Frontend yako kuwasiliana na hii Backend

# Weka API Key yako hapa au tumia Environment Variable (Inashauriwa zaidi)
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-22b7b924a538428ab952959c8c2022ec")
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# MAELEKEZO YA BOT (System Prompt)
SYSTEM_PROMPT = """
Wewe ni 'DSN ASSISTANT', mtoa huduma wa kidijitali wa kampuni ya DSN Technology.
Kazi yako ni kutoa huduma kwa Kiswahili na Kiingereza.

SHERIA KUU:
1. Jibu maswali yanayohusu DSN Technology TU. Usijibu kitu kingine chochote nje ya hapo.
2. Huduma zetu ni: [Taja huduma zako hapa - mfano: Graphics Design, Web Dev, Software, n.k].
3. Bei zetu ni: [Weka bei zako hapa kulingana na huduma].
4. Lengo lako ni kuelewa mteja anahitaji nini na kumpa majibu sahihi papo hapo.
5. Ikiwa mteja anahitaji msaada zaidi au anataka kulipa, mpe namba yetu ya WhatsApp: 0745720609.

Kuwa na adabu, mchangamfu, na mtaalamu.
"""

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            stream=False
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
