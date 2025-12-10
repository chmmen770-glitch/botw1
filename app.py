from flask import Flask, request, jsonify
import http.client
import urllib.parse
import ssl

app = Flask(__name__)

ULTRAMSG_INSTANCE_ID = "instance155419"
ULTRAMSG_TOKEN = "3y3jgb9grlw0aa6a"

# =========================
# פונקציות עזר
# =========================
def normalize_phone(phone):
    return ''.join(filter(str.isdigit, phone))

def send_whatsapp_message(to, message):
    try:
        to_normalized = normalize_phone(to)
        params = {
            "token": ULTRAMSG_TOKEN,
            "to": to_normalized,
            "body": message
        }
        payload = urllib.parse.urlencode(params)
        conn = http.client.HTTPSConnection("api.ultramsg.com", context=ssl._create_unverified_context())
        conn.request("POST", f"/{ULTRAMSG_INSTANCE_ID}/messages/chat", payload,
                     {"content-type": "application/x-www-form-urlencoded"})
        res = conn.getresponse()
        data = res.read()
        conn.close()
        print("SEND RESPONSE:", data.decode("utf-8"))
        return data.decode("utf-8")
    except Exception as e:
        print("SEND ERROR:", e)
        return None

# =========================
# שמירת מצב השיחה לפי משתמש
# =========================
user_states = {}

# =========================
# סדרת שאלות להזמנה
# =========================
questions = [
    "שלום! לאיזה סוג אירוע תרצה להזמין צלם? (חתונה, בר/בת מצווה, אירוע פרטי, אחר)",
    "תודה! מה תאריך האירוע? (יום/חודש/שנה)",
    "איפה יתקיים האירוע? כתובת מלאה או עיר",
    "כמה שעות היית רוצה שהצילום ימשך?",
    "איזה סגנון צילום מעניין אותך? (סטילס, וידאו, שניהם, אחר)",
    "נשמח לקבל שם ומספר טלפון ליצירת קשר",
    "האם יש משהו נוסף שחשוב לנו לדעת? (למשל רעיונות מיוחדים או בקשות מיוחדות)"
]

# =========================
# Webhook UltraMsg
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data or "data" not in data:
        return jsonify({"status": "error", "message": "No valid JSON received"}), 400

    sender = data["data"]["from"]
    message = data["data"]["body"]

    if sender not in user_states:
        # התחלת שיחה חדשה
        user_states[sender] = {"step": 0, "answers": {}}
        send_whatsapp_message(sender, questions[0])
        user_states[sender]["step"] = 1
        return jsonify({"status": "ok"}), 200

    state = user_states[sender]
    step = state["step"]

    # שמירת תשובה מהמשתמש
    if step > 0 and step <= len(questions):
        key = f"q{step}"
        state["answers"][key] = message

        if step == len(questions):
            # סיום סדרת השאלות
            summary = "תודה על המידע! הנה הסיכום של הזמנתך:\n\n"
            for i, ans in enumerate(state["answers"].values(), 1):
                summary += f"{i}. {ans}\n"
            send_whatsapp_message(sender, summary)
            # מחיקת מצב המשתמש או אפשר להשאיר
            user_states.pop(sender)
        else:
            # שליחת השאלה הבאה
            send_whatsapp_message(sender, questions[step])
            state["step"] += 1

    return jsonify({"status": "ok"}), 200

# =========================
# בדיקת שרת
# =========================
@app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200

# =========================
# הרצה
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
