from flask import Flask, request, jsonify
import requests
import re
import time

app = Flask(__name__)

# ================
# CONFIG
# ================
BOT_NUMBER = "13474528352"  # לתקן למספר שלך (רק ספרות)
ULTRAMSG_INSTANCE = "instance155419"
ULTRAMSG_TOKEN = "3y3jgb9grlw0aa6a"

# ============
# צבעים ללוג
# ============
CRED = "\033[91m"
CGREEN = "\033[92m"
CYELLOW = "\033[93m"
CBLUE = "\033[94m"
CEND = "\033[0m"


# ===================
# ניקוי מספרים
# ===================
def extract_numbers(text):
    return ''.join(filter(str.isdigit, str(text)))


# ===================
# שליחת הודעה
# ===================
def send_message(to, message):
    print(CBLUE + f"[SEND_MESSAGE] שולח ל-{to}: {message}" + CEND)

    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message
    }

    try:
        r = requests.post(url, data=payload)
        print(CBLUE + f"[SEND_MESSAGE_RESPONSE] {r.text}" + CEND)
    except Exception as e:
        print(CRED + f"[SEND_MESSAGE_ERROR] {e}" + CEND)


# ===================
# לוגיקה של הבוט
# ===================
def handle_message(sender, text):
    text = text.lower().strip()

    # בדיקה אם המשתמש שולח משהו
    print(CGREEN + f"[HANDLE_MESSAGE] הודעה מ-{sender}: {text}" + CEND)

    send_message(sender, f"Received: {text}")


# ===================
# WEBHOOK
# ===================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    print(CYELLOW + "\n=======================" + CEND)
    print(CYELLOW + "[WEBHOOK] קיבלנו בקשה חדשה" + CEND)
    print(CYELLOW + "=======================\n" + CEND)

    print(CYELLOW + f"[RAW DATA] {data}\n" + CEND)

    if not data or "data" not in data:
        print(CRED + "[ERROR] אין נתונים!" + CEND)
        return jsonify({"status": "error"}), 400

    d = data["data"]

    raw_sender = d.get("from")
    text = d.get("body", "")
    from_me = d.get("fromMe", False)

    print(CYELLOW + f"[SENDER RAW] {raw_sender}" + CEND)
    print(CYELLOW + f"[MESSAGE TEXT] {text}" + CEND)
    print(CYELLOW + f"[FROM_ME] {from_me}" + CEND)

    sender_digits = extract_numbers(raw_sender)
    bot_digits = extract_numbers(BOT_NUMBER)

    print(CYELLOW + f"[SENDER NORMALIZED] {sender_digits}" + CEND)
    print(CYELLOW + f"[BOT NORMALIZED] {bot_digits}\n" + CEND)

    # ==========================
    # שלב 1 – הודעה של הבוט עצמו לפי fromMe
    # ==========================
    if from_me is True:
        print(CRED + "[IGNORED] fromMe=True → זו הודעה של הבוט לעצמו" + CEND)
        return jsonify({"ignored": "from_me"}), 200

    # ==========================
    # שלב 2 – בדיקה לפי מספר
    # ==========================
    if sender_digits == bot_digits:
        print(CRED + "[IGNORED] המספר זהה למספר הבוט → הבוט שולח לעצמו" + CEND)
        return jsonify({"ignored": "self_number"}), 200

    # ==========================
    # שלב 3 – אם עברנו את כל הבדיקות, זו באמת הודעה של משתמש
    # ==========================
    print(CGREEN + "[VALID MESSAGE] זהו משתמש אמיתי → מעבד תשובה" + CEND)

    handle_message(sender_digits, text)
    return jsonify({"status": "ok"}), 200


@app.route("/", methods=["GET"])
def home():
    return "Bot running OK", 200


if __name__ == "__main__":
    print(CGREEN + ">> הבוט פועל ומחכה להודעות..." + CEND)
    app.run(host="0.0.0.0", port=5000)
