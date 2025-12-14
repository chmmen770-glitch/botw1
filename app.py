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
        "היי אהובה, וברוכה הבאה ל־Beauty Studio 💅\n"
        "אני כאן כדי לעזור לך 🌸\n\n"
        "על מה תרצי לשאול?\n"
        "1️⃣ 🕒 שעות פתיחה\n"
        "2️⃣ 🎓 קורסים והשתלמויות\n"
        "3️⃣ 📦 הזמנות ומשלוחים\n"
        "4️⃣ 💔 קיבלתי הזמנה פגומה\n"
        "5️⃣ 🛠️ אחריות ותיקונים\n\n"
        "שלחי מספר / שם נושא\n"
        "או כתבי *תפריט* בכל שלב לחזרה 💕"
    )

# ===================
# לוגיקה של שיחה
# ===================
def handle_message(sender, text):
    text_clean = text.lower().strip()
    print(CGREEN + f"[HANDLE_MESSAGE] מ-{sender}: {text_clean}" + CEND)

    if sender not in user_states:
        user_states[sender] = {"stage": "menu"}
        send_main_menu(sender)
        return

    # חזרה לתפריט מכל מקום
    if text_clean == "תפריט":
        user_states[sender]["stage"] = "menu"
        send_main_menu(sender)
        return

    stage = user_states[sender]["stage"]

    # ===== תפריט ראשי =====
    if stage == "menu":

        if text_clean in ["1", "שעות פתיחה"]:
            user_states[sender]["stage"] = "opening_hours"
            send_message(
                sender,
                "🕒 *שעות פתיחה*\n"
                "ימים א׳–ה׳: 09:00–18:00\n"
                "יום ו׳: 09:00–13:00\n\n"
                "☎️ טלפון: 050-0000000\n\n"
                "לכל דבר נוסף – כתבי *תפריט* 💕"
            )

        elif text_clean in ["2", "קורסים", "קורסים והשתלמויות"]:
            user_states[sender]["stage"] = "courses_type"
            send_message(
                sender,
                "איזה סוג קורס מעניין אותך?\n"
                "💻 קורסים דיגיטליים\n"
                "🏫 קורסים פרונטליים\n\n"
                "או *תפריט* לחזרה 🌸"
            )

        elif text_clean in ["3", "הזמנות", "משלוחים"]:
            user_states[sender]["stage"] = "orders_menu"
            send_message(
                sender,
                "📦 הזמנות ומשלוחים\n"
                "על מה תרצי לשאול?\n"
                "🚚 זמני משלוח ועלויות\n"
                "📦 מעקב אחרי הזמנה\n\n"
                "או *תפריט* לחזרה"
            )

        elif text_clean in ["4", "הזמנה פגומה", "פגומה"]:
            user_states[sender]["stage"] = "damaged_order"
            send_message(
                sender,
                "מצטערות לשמוע שזה קרה 🥺\n\n"
                "כדי שנוכל לעזור, אנא שלחי:\n"
                "• שם מלא\n"
                "• מספר הזמנה (אם יש)\n"
                "• תיאור התקלה\n"
                "• ואם אפשר – תמונה של המוצר\n\n"
                "או *תפריט* לחזרה 💛"
            )

        elif text_clean in ["5", "אחריות", "תיקונים"]:
            user_states[sender]["stage"] = "warranty"
            send_message(
                sender,
                "🛠️ אחריות ותיקונים\n"
                "אנא שלחי:\n"
                "• על איזה מוצר מדובר\n"
                "• מתי נרכש (בערך)\n"
                "• מה הבעיה\n\n"
                "או *תפריט* לחזרה 🌸"
            )

        else:
            send_main_menu(sender)

    # ===== קורסים =====
    elif stage == "courses_type":

        if "דיגיטל" in text_clean:
            user_states[sender]["stage"] = "menu"
            send_message(
                sender,
                "💻 *קורסים דיגיטליים*\n"
                "למידה מהבית, בקצב שלך, עם גישה לשיעורים 24/7.\n\n"
                "🔗 להרשמה ופרטים:\n"
                "https://example.com\n\n"
                "לשיחה נוספת – *תפריט* 💕"
            )

        elif "פרונט" in text_clean:
            user_states[sender]["stage"] = "menu"
            send_message(
                sender,
                "🏫 *קורסים פרונטליים*\n"
                "לימוד מעשי עם ליווי אישי בקבוצות קטנות.\n\n"
                "לפרטים – שלחי:\n"
                "שם מלא + טלפון 📞\n\n"
                "או *תפריט* לחזרה"
            )

        else:
            send_message(
                sender,
                "אנא בחרי:\n"
                "💻 קורסים דיגיטליים\n"
                "🏫 קורסים פרונטליים\n"
                "או *תפריט*"
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

