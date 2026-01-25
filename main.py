import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# 1. Kupata API Key kutoka kwenye Environment Variables (Railway)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Angalia kama API Keyipo
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY haijawekwa kwenye environment variables.")

# Konfigura Gemini AI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Maelekezo ya Bot (System Instructions)
# Hapa ndipo tunapomfundisha AI jinsi ya kuwa DSN ASSISTANT
SYSTEM_INSTRUCTION = """
Wewe ni 'DSN ASSISTANT', mtoa huduma msaidizi wa kampuni ya DSN.
Lugha yako ni Kiswahili fasaha, rafiki na la kibiashara.

HUDUMA TUNAZOTOA MTANDAONI:
1. Graphic Design (Logo, Mabango, Flyers).
2. Web Design & Development (Tovuti za biashara na binafsi).
3. Social Media Management (Kusimamia kurasa za mitandao).
4. Digital Marketing & Sponsored Ads.
5. Huduma za TEHAMA na Ushauri.

KANUNI MUHIMU:
- Jibu maswali yanayohusu huduma zetu tu.
- Ukiulizwa kuhusu bei, sema bei inategemea ukubwa wa kazi na waombe wasiliane na admin.
- Ikiwa huwezi kujibu swali au mteja anahitaji kuongea na binadamu, mpe namba hii ya Admin.
- NAMBA YA ADMIN (WHATSAPP): 0745720709.
- Usitoe majibu ya uongo.

Jibu kwa ufupi na unyenyekevu.
"""

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "Online",
        "message": "DSN Assistant iko tayari kuhudumia via API."
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')

        if not user_message:
            return jsonify({"error": "Tafadhali andika ujumbe wako."}), 400

        # Unganisha maelekezo ya system na ujumbe wa mteja
        full_prompt = f"{SYSTEM_INSTRUCTION}\n\nSwali la Mteja: {user_message}\nJibu la DSN ASSISTANT:"

        # Tuma kwa Gemini
        response = model.generate_content(full_prompt)
        
        return jsonify({
            "response": response.text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Railway inahitaji port maalum, default ni 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
