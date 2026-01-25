import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Weka API Key yako hapa (au itumie kama Environment Variable kwenye Render)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Maelekezo kwa AI kuhusu kampuni yako
SYSTEM_PROMPT = """
Wewe ni DSN ASSISTANT, mtoa huduma wa kampuni ya DSN. 
Kazi yako ni kujibu maswali kuhusu huduma tunazotoa mtandaoni kwa ukarimu na weledi.
Kama mteja anahitaji msaada wa karibu au kuzungumza na binadamu, mpe namba ya WhatsApp ya Admin: 0745720709.
Lugha kuu ni Kiswahili na Kiingereza.
"""

model = genai.GenerativeModel('gemini-pro')

# HTML Rahisi kwa ajili ya Muonekano (Frontend)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DSN ASSISTANT</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #f4f4f4; padding: 20px; }
        .chat-box { max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input { width: 80%; padding: 10px; border: 1px solid #ddd; }
        button { padding: 10px; background: #25d366; color: white; border: none; cursor: pointer; }
        #response { margin-top: 20px; white-space: pre-wrap; color: #333; }
    </style>
</head>
<body>
    <div class="chat-box">
        <h2>DSN ASSISTANT 🤖</h2>
        <p>Karibu! Uliza chochote kuhusu huduma zetu.</p>
        <input type="text" id="userInput" placeholder="Andika hapa...">
        <button onclick="askAI()">Tuma</button>
        <div id="response"></div>
        <hr>
        <p><small>WhatsApp Admin: <a href="https://wa.me/255745720709">0745720709</a></small></p>
    </div>

    <script>
        async function askAI() {
            const input = document.getElementById('userInput').value;
            const resDiv = document.getElementById('response');
            resDiv.innerText = "Inafikiri...";
            
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: input})
            });
            const data = await response.json();
            resDiv.innerText = data.reply;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', method=['POST'])
def chat():
    user_message = request.json.get("message")
    full_prompt = f"{SYSTEM_PROMPT}\n\nMteja anasema: {user_message}"
    
    try:
        response = model.generate_content(full_prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": "Samahani, kuna tatizo la kiufundi. Jaribu tena baadae."})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
