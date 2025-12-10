from flask import Flask, request, jsonify
import http.client
import ssl
import urllib.parse

app = Flask(__name__)

# --- CONFIG UltraMsg ---
TOKEN = "3y3jgb9grlw0aa6a"        # החלף ב‑Token שלך
INSTANCE_ID = "instance155419"     # החלף ב‑Instance שלך
API_URL = f"/{INSTANCE_ID}/messages/chat"

# --- שאלות ---
questions = [
    {'key': 'name', 'question': 'מה שמך המלא?'},
    {'key': 'date', 'question': 'באיזה תאריך האירוע?'},
    {'key': 'eventType', 'question': 'מה סוג האירוע?'},
    {'key': 'location', 'question': 'מה מקום האירוע?'},
    {'key': 'phone', 'question': 'מה מספר הטלפון שלך?'}
]

# --- Sessions לכל משתמש ---
sessions = {}

# --- פונקציה לשליחת הודעה דרך UltraMsg ---
def send_message(to, text):
    conn = http.client.HTTPSConnection("api.ultramsg.com", context=ssl._create_unverified_context())
    payload = f"token={TOKEN}&to={urllib.parse.quote(to)}&body={urllib.parse.quote(text)}"
    headers = {'content-type': "application/x-www-form-urlencoded"}
    conn.request("POST", API_URL, payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(f"Sent to {to}: {text}")
    print(data.decode("utf-8"))

# --- טיפול בהודעות נכנסות ---
def handle_message(from_number, text):
    text = text.strip().lower()

    if from_number not in sessions:
        sessions[from_number] = {'step': 0, 'answers': {}}
        send_message(from_number, "👋 שלום! רוצה להזמין צלם לאירוע? כתוב 'כן' כדי להתחיל.")
        return

    session = sessions[from_number]

    if session['step'] == 0:
        if text == 'כן':
            send_message(from_number, questions[0]['question'])
            session['step'] = 1
        else:
            send_message(from_number, "כתוב 'כן' כדי להתחיל את הזמנת הצלם.")
        return

    if 1 <= session['step'] <= len(questions):
        q = questions[session['step']-1]
        session['answers'][q['key']] = text

        if session['step'] < len(questions):
            send_message(from_number, questions[session['step']]['question'])
            session['step'] += 1
        else:
            summary = "📄 סיכום ההזמנה שלך:\n\n"
            for q in questions:
                summary += f"{q['question']} {session['answers'][q['key']]}\n"
            send_message(from_number, summary)
            del sessions[from_number]

# --- Webhook Endpoint ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({"status": "no data"}), 400

    # UltraMsg שולח את מספר השולח וההודעה ב‑JSON
    from_number = data.get('from')
    message_text = data.get('body')

    if from_number and message_text:
        handle_message(from_number, message_text)

    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
