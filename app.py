from flask import Flask, request, jsonify
import requests
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# ================= CONFIG =================
BOT_NUMBER = "13474528352"
ADMIN_NUMBER = "13474528352"

ULTRAMSG_INSTANCE = "instance155419"
ULTRAMSG_TOKEN = "3y3jgb9grlw0aa6a"

ADMIN_EMAIL = "chmmen770@gmail.com"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "chmmen770@gmail.com"
EMAIL_PASSWORD = "cjmj xsgk aicv gxwm"

user_states = {}

# ================= UTILS =================
def extract_numbers(text):
    return ''.join(filter(str.isdigit, str(text)))

def send_message(to, message):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message
    }
    requests.post(url, data=payload, timeout=10)

def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = ADMIN_EMAIL
# 
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("EMAIL ERROR:", e)

# ================= MENU =================
def send_main_menu(sender):
    send_message(
        sender,
        "היי אהובה, וברוכה הבאה ל־Beauty Studio 💅\n"
        "איך אוכל לעזור? 🌸\n\n"
        "1️⃣ 📦 הזמנות ומשלוחים\n"
        "2️⃣ 🛠️ אחריות / תיקונים / מוצר פגום\n\n"
        "כתבי מספר או *תפריט* 💕"
    )

# ================= LOGIC =================
def handle_message(sender, text, media_link=""):
    text_clean = text.lower().strip()

    if sender not in user_states:
        user_states[sender] = {"stage": "menu"}
        send_main_menu(sender)
        return

    if text_clean == "תפריט":
        user_states[sender] = {"stage": "menu"}
        send_main_menu(sender)
        return

    stage = user_states[sender]["stage"]

    # ===== MENU =====
    if stage == "menu":

        if text_clean in ["1", "הזמנות", "משלוחים", "הזמנות ומשלוחים"]:
            user_states[sender]["stage"] = "orders_menu"
            send_message(
                sender,
                "📦 הזמנות ומשלוחים\n"
                "על מה תרצי לשאול?\n"
                "🚚 זמני משלוח ועלויות\n"
                "📦 מעקב אחרי הזמנה\n\n"
                "*תפריט* לחזרה"
            )

        elif text_clean in ["2", "אחריות", "תיקונים", "פגום", "פגומה"]:
            user_states[sender]["stage"] = "warranty"
            send_message(
                sender,
                "כדי שנוכל לטפל בפנייה שלך בצורה הטובה ביותר 🌸\n"
                "אנא שלחי:\n\n"
                "• שם מלא\n"
                "• מספר הזמנה (אם יש)\n"
                "• על איזה מוצר מדובר\n"
                "• תיאור הבעיה\n"
                "• תמונה (אם יש)\n\n"
                "בסיום נשלח אלייך סיכום 💛\n"
                "*תפריט* לחזרה"
            )

        else:
            send_main_menu(sender)

    # ===== ORDERS MENU =====
    elif stage == "orders_menu":
        if "זמני" in text_clean or "משלוח" in text_clean:
            send_message(
                sender,
                "🚚 זמני משלוח ועלויות:\n"
                "זמן אספקה: 3–5 ימי עסקים\n"
                "עלות משלוח: 35₪\n\n"
                "*תפריט*"
            )

        elif "מעקב" in text_clean:
            send_message(
                sender,
                "📦 מעקב אחרי הזמנה\n"
                "שלחי מספר הזמנה או שם מלא\n\n"
                "*תפריט*"
            )

        else:
            send_message(
                sender,
                "אנא בחרי:\n"
                "🚚 זמני משלוח ועלויות\n"
                "📦 מעקב אחרי הזמנה\n\n"
                "*תפריט*"
            )

    # ===== WARRANTY / REPAIR =====
    elif stage == "warranty":

        summary = (
            "🛠️ פנייה חדשה – אחריות / תיקון / מוצר פגום\n\n"
            f"📞 טלפון: {sender}\n\n"
            f"📝 פרטי הלקוחה:\n{text}"
        )

        if media_link:
            summary += f"\n\n📸 תמונה:\n{media_link}"

        send_message(ADMIN_NUMBER, summary)
        send_email("פנייה חדשה – אחריות / תיקון", summary)

        # סיכום ללקוחה
        send_message(
            sender,
            "💛 סיכום הבקשה שלך:\n\n"
            "סוג פנייה: אחריות / תיקון / מוצר פגום\n"
            f"טלפון: {sender}\n"
            f"פרטים שנשלחו:\n{text}\n\n"
            "הפנייה נקלטה בהצלחה 🌸\n"
            "נחזור אלייך בהקדם 💅\n\n"
            "*תפריט*"
        )

        user_states[sender] = {"stage": "menu"}

# ================= WEBHOOK =================
@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    # ===== אימות (GET) =====
    if request.method == "GET":
        token_sent = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token_sent == "mytoken123":
            return challenge or "OK", 200
        else:
            return "Verification failed", 403

    # ===== הודעות רגילות (POST) =====
    data = request.get_json(silent=True)

    if not data or "data" not in data:
        return jsonify({"status": "error"}), 400

    d = data["data"]

    sender = extract_numbers(d.get("from", ""))
    text = d.get("body", "")
    from_me = d.get("fromMe", False)

    media = d.get("media", None)
    media_link = ""
    if isinstance(media, dict):
        media_link = media.get("link", "")

    if from_me:
        return jsonify({"ignored": True}), 200

    handle_message(sender, text, media_link)
    return jsonify({"status": "ok"}), 200
def webhook():
    data = request.get_json(silent=True)

    if not data or "data" not in data:
        return jsonify({"status": "error"}), 400

    d = data["data"]

    sender = extract_numbers(d.get("from", ""))
    text = d.get("body", "")
    from_me = d.get("fromMe", False)

    media = d.get("media", None)
    media_link = ""
    if isinstance(media, dict):
        media_link = media.get("link", "")

    if from_me:
        return jsonify({"ignored": True}), 200

    handle_message(sender, text, media_link)
    return jsonify({"status": "ok"}), 200

@app.route("/")
def home():
    return "Bot running OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


