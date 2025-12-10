from flask import Flask, request, jsonify
import http.client
import ssl

app = Flask(__name__)

# 🔹 רשימת השאלות
questions = [
    {"key": "name", "question": "מה שמך המלא?"},
    {"key": "date", "question": "באיזה תאריך האירוע?"},
    {"key": "eventType", "question": "מה סוג האירוע?"},
    {"key": "location", "question": "מה מקום האירוע?"},
    {"key": "phone", "question": "מה מספר הטלפון שלך?"}
]

# 🔹 שמירת session לכל משתמש לפי מספר
sessions = {}

# 🔹 פרטי UltraMsg שלך
INSTANCE_ID = "instance155419"
TOKEN = "3y3jgb9grlw0aa6a"

def send_message(to, body):
    conn = http.client.HTTPSConnection("api.ultramsg.com", context=ssl._create_unverified_context())
    payload = f"token={TOKEN}&to={to}&body={body}"
    payload = payload.encode('utf8').decode('iso-8859-1')
    headers = {'content-type': "application/x-www-form-urlencoded"}
    conn.request("POST", f"/{INSTANCE_ID}/messages/chat", payload, headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    return data.decode("utf-8")

@app.route("/webhook", methods=["POST"])
def handle_message():
    data = request.json

    # 🔹 UltraMsg שולח פרטי הודעה
    from_number = data.get("from")
    message_body = data.get("body", "").strip()

    if not from_number or not message_body:
        return jsonify({"status": "no data"}), 400

    # 🔹 בדיקה אם המספר כבר במערכת
    if from_number not in sessions:
        # יצירת session חדש
        sessions[from_number] = {"step": 0, "answers": {}}
        send_message(from_number, "👋 שלום! רוצה להזמין צלם לאירוע? כתוב 'כן' כדי להתחיל.")
        return jsonify({"status": "started"}), 200

    session = sessions[from_number]
    step = session["step"]

    # 🔹 התחלת התהליך
    if step == 0 and message_body.lower() == "כן":
        send_message(from_number, questions[0]["question"])
        session["step"] = 1
        return jsonify({"status": "question sent"}), 200

    # 🔹 אם כבר בתוך התהליך
    if 0 < step <= len(questions):
        # שמירת תשובה קודמת
        session["answers"][questions[step - 1]["key"]] = message_body

        if step < len(questions):
            # שליחת השאלה הבאה
            send_message(from_number, questions[step]["question"])
            session["step"] += 1
        else:
            # סוף התהליך – סיכום ההזמנה
            summary = "📄 סיכום ההזמנה שלך:\n\n"
            for q in questions:
                summary += f"{q['question']} {session['answers'][q['key']]}\n"

            send_message(from_number, summary)
            # מחיקת session
            del sessions[from_number]

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # Flask מתחיל להריץ את השרת
    app.run(host="0.0.0.0", port=5000)
