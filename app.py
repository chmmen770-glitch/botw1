from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ================
# CONFIG
# ================
BOT_NUMBER = "13474528352"
ADMIN_NUMBER = "13474528352"

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
    print(CBLUE + f"[SEND_MESSAGE] אל {to}: {message}" + CEND)

    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message
    }

    try:
        requests.post(url, data=payload, timeout=10)
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
        "שלחי מספר או שם נושא\n"
        "או כתבי *תפריט* בכל שלב 💕"
    )

# ===================
# לוגיקה של שיחה
# ===================
def handle_message(sender, text, media_link=""):
    text_clean = text.lower().strip()
    print(CGREEN + f"[HANDLE_MESSAGE] {sender}: {text_clean}" + CEND)

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
                "🕒 שעות פתיחה:\n"
                "א׳–ה׳ 09:00–18:00\n"
                "ו׳ 09:00–13:00\n\n"
                "☎️ 050-0000000\n\n"
                "*תפריט* לחזרה 💕"
            )

        elif text_clean in ["2", "קורסים", "קורסים והשתלמויות"]:
            user_states[sender]["stage"] = "courses"
            send_message(
                sender,
                "איזה סוג קורס מעניין אותך?\n"
                "💻 קורסים דיגיטליים\n"
                "🏫 קורסים פרונטליים\n\n"
                "*תפריט* לחזרה"
            )

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

        elif text_clean in ["4", "פגומה", "הזמנה פגומה"]:
            user_states[sender]["stage"] = "damaged_order"
            send_message(
                sender,
                "מצטערות לשמוע שזה קרה 🥺\n\n"
                "אנא שלחי:\n"
                "• שם מלא\n"
                "• מספר הזמנה (אם יש)\n"
                "• תיאור התקלה\n"
                "• ואם אפשר – תמונה\n\n"
                "*תפריט* לחזרה 💛"
            )

        elif text_clean in ["5", "אחריות", "תיקונים"]:
            user_states[sender]["stage"] = "warranty"
            send_message(
                sender,
                "🛠️ אחריות ותיקונים\n"
                "אנא שלחי:\n"
                "• מוצר\n"
                "• מועד רכישה (בערך)\n"
                "• מה הבעיה\n\n"
                "*תפריט* לחזרה 🌸"
            )

        else:
            send_main_menu(sender)

    # ===== הזמנות =====
    elif stage == "orders_menu":

        if "זמני" in text_clean or "עלות" in text_clean:
            send_message(
                sender,
                "🚚 משלוחים:\n"
                "זמן אספקה: 3–7 ימי עסקים\n"
                "עלות: 35₪ | חינם מעל 299₪\n\n"
                "*תפריט* לחזרה"
            )

        elif "מעקב" in text_clean:
            user_states[sender]["stage"] = "order_tracking"
            send_message(
                sender,
                "📦 מעקב אחרי הזמנה\n"
                "אנא שלחי מספר הזמנה או פרטים מזהים 💕\n\n"
                "*תפריט* לחזרה"
            )

        else:
            send_message(sender, "אנא בחרי אחת מהאפשרויות 👆")

    # ===== מעקב הזמנה =====
    elif stage == "order_tracking":

        send_message(
            ADMIN_NUMBER,
            f"📦 פנייה – מעקב הזמנה\n"
            f"📞 {sender}\n"
            f"📝 {text}"
        )

        send_message(
            sender,
            "קיבלנו 💕 נבדוק ונחזור אלייך בהקדם.\n\n*תפריט*"
        )

        user_states[sender]["stage"] = "menu"

    # ===== הזמנה פגומה =====
    elif stage == "damaged_order":

        msg = (
            "💔 פנייה – הזמנה פגומה\n"
            f"📞 {sender}\n"
            f"📝 {text}"
        )

        if media_link:
            msg += f"\n📷 תמונה:\n{media_link}"

        send_message(ADMIN_NUMBER, msg)

        send_message(
            sender,
            "תודה ששלחת 💛 נחזור אלייך בהקדם.\n\n*תפריט*"
        )

        user_states[sender]["stage"] = "menu"

    # ===== אחריות =====
    elif stage == "warranty":

        send_message(
            ADMIN_NUMBER,
            f"🛠️ פנייה – אחריות\n"
            f"📞 {sender}\n"
            f"📝 {text}"
        )

        send_message(
            sender,
            "קיבלנו 🌸 נחזור אלייך בהקדם.\n\n*תפריט*"
        )

        user_states[sender]["stage"] = "menu"

# ===================
# WEBHOOK
# ===================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    print(CYELLOW + f"[WEBHOOK] {data}" + CEND)

    if not data or "data" not in data:
        return jsonify({"status": "error"}), 400

    d = data["data"]
    raw_sender = d.get("from", "")
    text = d.get("body", "")
    from_me = d.get("fromMe", False)

    media_link = ""
    if d.get("media"):
        media_link = d["media"].get("link", "")

    sender = extract_numbers(raw_sender)
    bot = extract_numbers(BOT_NUMBER)

    if from_me or sender == bot:
        return jsonify({"ignored": True}), 200

    handle_message(sender, text, media_link)
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
