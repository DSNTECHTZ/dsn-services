flask
google-genai
gunicorn

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
