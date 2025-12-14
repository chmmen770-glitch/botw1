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

# ===== EMAIL CONFIG =====
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "chmmen770@gmail.com"          # ⚠️ לשים מייל שולח
EMAIL_PASSWORD = "cjmj xsgk aicv gxwm"       # ⚠️ סיסמת אפליקציה

# ================= STATES =================
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
        "1️⃣ 🕒 שעות פתיחה\n"
        "2️⃣ 🎓 קורסים והשתלמויות\n"
        "3️⃣ 📦 הזמנות ומשלוחים\n"
        "4️⃣ 💔 קיבלתי הזמנה פגומה\n"
        "5️⃣ 🛠️ אחריות ותיקונים\n\n"
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
        user_states[sender]["stage"] = "menu"
        send_main_menu(sender)
        return

    stage = user_states[sender]["stage"]

    # ===== MENU =====
    if stage == "menu":

        # ✅ שעות פתיחה
        if text_clean in ["1", "שעות פתיחה"]:
            send_message(
                sender,
                "🕒 שעות פתיחה:\n"
                "א׳–ה׳ 09:00–18:00\n"
                "ו׳ 09:00–13:00\n\n"
                "☎️ 050-0000000\n\n"
                "*תפריט* לחזרה 💕"
            )

        # ✅ קורסים
        elif text_clean in ["2", "קורסים"]:
            user_states[sender]["stage"] = "courses"
            send_message(
                sender,
                "איזה סוג קורס מעניין אותך?\n"
                "💻 קורסים דיגיטליים\n"
                "🏫 קורסים פרונטליים\n\n"
                "*תפריט* לחזרה"
            )

        # ✅ הזמנות ומשלוחים
        elif text_clean in ["3", "הזמנות", "משלוחים", "הזמנות ומשלוחים"]:
            user_states[sender]["stage"] = "orders_menu"
            send_message(
                sender,
                "📦 הזמנות ומשלוחים\n"
                "על מה תרצי לשאול?\n"
                "🚚 זמני משלוח ועלויות\n"
                "📦 מעקב אחרי הזמנה\n\n"
                "*תפריט* לחזרה"
            )

        elif text_clean in ["4", "פגומה"]:
            user_states[sender]["stage"] = "damaged"
            send_message(
                sender,
                "מצטערות לשמוע שזה קרה 🥺\n"
                "שלחי:\n"
                "• שם מלא\n"
                "• מספר הזמנה\n"
                "• תיאור\n"
                "• תמונה (אם יש)\n\n"
                "*תפריט*"
            )

        elif text_clean in ["5", "אחריות"]:
            user_states[sender]["stage"] = "warranty"
            send_message(
                sender,
                "אנא שלחי:\n"
                "• מוצר\n"
                "• מועד רכישה\n"
                "• מה הבעיה\n\n"
                "*תפריט*"
            )

        else:
            send_main_menu(sender)

    # ===== COURSES =====
    elif stage == "courses":

        if "דיגיטל" in text_clean:
            send_message(
                sender,
                "💻 קורסים דיגיטליים\n"
                "למידה מהבית, גישה 24/7.\n"
                "לפרטים:\nhttps://example.com\n\n"
                "*תפריט*"
            )

        elif "פרונט" in text_clean:
            user_states[sender]["stage"] = "waiting_course_lead"
            send_message(
                sender,
                "🏫 קורסים פרונטליים\n"
                "ליווי אישי ותרגול מעשי.\n"
                "שלחי שם + טלפון ונחזור אלייך 💕\n\n"
                "*תפריט*"
            )

        else:
            send_message(sender, "אנא בחרי דיגיטליים או פרונטליים 💅")

    # ===== WAITING COURSE LEAD – שם + טלפון פרונטלי =====
    elif stage == "waiting_course_lead":
        summary = f"📚 ליד קורס פרונטלי חדש:\n📞 מ-{sender}\n📝 פרטים:\n{text}"
        send_message(ADMIN_NUMBER, summary)
        send_email("קורס פרונטלי חדש", summary)
        user_states[sender]["stage"] = "menu"
        send_message(
            sender,
            "קיבלנו 🌸\nנחזור אלייך בהקדם.\n\n*תפריט*"
        )

    # ===== DAMAGED =====
    elif stage == "damaged":
        summary = f"💔 הזמנה פגומה\nטלפון: {sender}\nתוכן:\n{text}"
        if media_link:
            summary += f"\nתמונה:\n{media_link}"
        send_message(ADMIN_NUMBER, summary)
        send_email("הזמנה פגומה", summary)
        send_message(sender, "קיבלנו 🌸\nנחזור אלייך בהקדם.\n\n*תפריט*")
        user_states[sender]["stage"] = "menu"

    # ===== WARRANTY =====
    elif stage == "warranty":
        summary = f"🛠️ אחריות / תיקון\nטלפון: {sender}\nתוכן:\n{text}"
        send_message(ADMIN_NUMBER, summary)
        send_email("אחריות / תיקונים", summary)
        send_message(sender, "קיבלנו 🌸\nנחזור אלייך בהקדם.\n\n*תפריט*")
        user_states[sender]["stage"] = "menu"

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

# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data or "data" not in data:
        return jsonify({"status": "error"}), 400

    d = data["data"]

    sender = extract_numbers(d.get("from", ""))
    text = d.get("body", "")
    from_me = d.get("fromMe", False)

    # טיפול נכון במדיה
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
