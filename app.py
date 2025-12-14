from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ================
# CONFIG
# ================
BOT_NUMBER = "13474528352"
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
# מצבי שיחה (זמני – בזיכרון)
# ===================
user_states = {}

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
        r = requests.post(url, data=payload, timeout=10)
        print(CBLUE + f"[SEND_MESSAGE_RESPONSE] {r.text}" + CEND)
    except Exception as e:
        print(CRED + f"[SEND_MESSAGE_ERROR] {e}" + CEND)

# ===================
# תפריט ראשי
# ===================
def send_main_menu(sender):
    send_message(
        sender,
        "היי אהובה, וברוכה הבאה ל-[שם העסק שלך] 💅\n"
        "אני הבוט של [השם שלך] ואשמח לעזור לך 🌸\n\n"
        "על מה תרצי לשאול?\n"
        "1️⃣ 🕒 שעות פתיחה\n"
        "2️⃣ 🎓 קורסים והשתלמויות\n"
        "שלחי את המספר או את שם הנושא 💬"
    )

# ===================
# לוגיקה של שיחה
# ===================
def handle_message(sender, text):
    text_clean = text.lower().strip()
    print(CGREEN + f"[HANDLE_MESSAGE] מ-{sender}: {text_clean}" + CEND)

    # אתחול משתמש אם לא קיים
    if sender not in user_states:
        user_states[sender] = {"stage": "menu"}

    stage = user_states[sender]["stage"]

    # ---------- תפריט ראשי ----------
    if stage == "menu":
        if text_clean in ["1", "שעות פתיחה"]:
            user_states[sender]["stage"] = "opening_hours"
            send_message(
                sender,
                "🕒 שעות פתיחה:\n"
                "ימים א׳–ה׳: 09:00–18:00\n"
                "☎️ טלפון: 050-0000000\n\n"
                "כדי לחזור לתפריט – שלחי 'תפריט'"
            )

        elif text_clean in ["2", "קורסים"]:
            user_states[sender]["stage"] = "courses_type"
            send_message(
                sender,
                "איזה סוג קורס מעניין אותך?\n"
                "💻 קורסים דיגיטליים\n"
                "🏫 קורסים פרונטליים"
            )

        else:
            send_main_menu(sender)

    # ---------- שעות פתיחה ----------
    elif stage == "opening_hours":
        if "תפריט" in text_clean:
            user_states[sender]["stage"] = "menu"
            send_main_menu(sender)
        else:
            send_message(sender, "אם תרצי לחזור – שלחי 'תפריט' 🌸")

    # ---------- סוג קורס ----------
    elif stage == "courses_type":
        if "דיגיטל" in text_clean:
            user_states[sender]["stage"] = "menu"
            send_message(
                sender,
                "💻 הקורסים הדיגיטליים זמינים לצפייה מכל מקום ובכל זמן.\n"
                "לפרטים והרשמה: [קישור]\n\n"
                "שלחי 'תפריט' להמשך"
            )

        elif "פרונט" in text_clean:
            user_states[sender]["stage"] = "menu"
            send_message(
                sender,
                "🏫 הקורסים הפרונטליים מתקיימים בליווי אישי.\n"
                "שלחי שם מלא + טלפון ונציג יחזור אלייך 💖"
            )

        else:
            send_message(
                sender,
                "אנא בחרי:\n"
                "💻 קורסים דיגיטליים\n"
                "🏫 קורסים פרונטליים"
            )

# ===================
# WEBHOOK
# ===================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    print(CYELLOW + "\n========== WEBHOOK ==========" + CEND)
    print(CYELLOW + f"[RAW DATA] {data}" + CEND)

    if not data or "data" not in data:
        return jsonify({"status": "error"}), 400

    d = data["data"]
    raw_sender = d.get("from", "")
    text = d.get("body", "")
    from_me = d.get("fromMe", False)

    sender_digits = extract_numbers(raw_sender)
    bot_digits = extract_numbers(BOT_NUMBER)

    if from_me or sender_digits == bot_digits:
        print(CRED + "[IGNORED] הודעה של הבוט עצמו" + CEND)
        return jsonify({"ignored": True}), 200

    handle_message(sender_digits, text)
    return jsonify({"status": "ok"}), 200

# ===================
# HEALTH CHECK
# ===================
@app.route("/", methods=["GET"])
def home():
    return "Bot running OK", 200

if __name__ == "__main__":
    print(CGREEN + ">> הבוט פועל ומחכה להודעות..." + CEND)
    app.run(host="0.0.0.0", port=5000)
