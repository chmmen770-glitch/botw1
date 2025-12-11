from flask import Flask, request, jsonify
import http.client
import urllib.parse
import ssl

app = Flask(__name__)

# =========================
# הגדרות חשבון UltraMsg
# =========================
ULTRAMSG_INSTANCE_ID = "instance155419"
ULTRAMSG_TOKEN = "3y3jgb9grlw0aa6a"
BOT_NUMBER = "13474528352"  # כאן הכנס את מספר הבוט שלך (כולל קידומת מדינה, רק ספרות)

# =========================
# הגדרות / תוכן שניתן לערוך
# =========================
BUSINESS_NAME = "[שם העסק שלך]"  # ערוך לשם העסק
OPENING_HOURS_TEXT = (
    "שעות פתיחה של " + BUSINESS_NAME + ":\n\n"
    "🏬 חנות:\n"
    "  - ב׳–ה׳: 09:00 — 18:00\n"
    "  - ו׳: 09:00 — 14:00\n"
    "  - שבת: סגור\n\n"
    "☎️ טלפון לחנות: 03-xxxxxxx\n\n"
    "האם תרצה לדעת משהו נוסף? (הקלד מספר מהתפריט או כתב שאלתך)"
)

MAIN_MENU_TEXT = (
    f"שלום! ברוך הבא ל־{BUSINESS_NAME} 👋\n\n"
    "על מה תרצה לשאול?\n\n"
    "1. 🕒 שעות פתיחה\n"
    "2. 🎓 קורסים והשתלמויות\n"
    "3. 📦 הזמנות ומשלוחים\n"
    "4. 💔 קיבלתי הזמנה פגומה\n"
    "5. 🛠️ אחריות ותיקונים\n\n"
    "ענה במספר המתאים או כתוב בקצרה מה תרצה לבדוק."
)

# =========================
# פונקציות עזר
# =========================
def normalize_phone(phone):
    """שומר רק ספרות ממספר טלפון"""
    return ''.join(filter(str.isdigit, str(phone)))

def send_whatsapp_message(to, message):
    """שולח הודעה דרך UltraMsg"""
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
# זיהוי כוונה פשוט
# =========================
def detect_intent(message):
    m = message.strip().lower()
    if m in ("1", "שעות", "שעות פתיחה", "מתי", "מתי אתם פתוחים", "מתי פתוח"):
        return "opening_hours"
    if m in ("2", "קורסים", "קורסים והשתלמויות", "השתלמויות"):
        return "courses"
    if m in ("3", "הזמנות", "משלוחים", "מעקב"):
        return "orders"
    if m in ("4", "פגומה", "הזמנה פגומה", "קיבלתי פגומה"):
        return "damaged"
    if m in ("5", "אחריות", "תיקונים"):
        return "warranty"
    if any(w in m for w in ["מתי", "שעות", "פתוח"]):
        return "opening_hours"
    return None

# =========================
# עיבוד הודעה
# =========================
def handle_message(sender, message):
    if sender not in user_states:
        user_states[sender] = {"step": 0, "mode": None, "answers": {}}
        send_whatsapp_message(sender, MAIN_MENU_TEXT)
        user_states[sender]["step"] = 1
        return

    state = user_states[sender]
    intent = detect_intent(message)

    if intent == "opening_hours":
        send_whatsapp_message(sender, OPENING_HOURS_TEXT)
        send_whatsapp_message(sender, "רוצה לחזור לתפריט הראשי? (כן/לא)")
        state["mode"] = None
        state["step"] = 1
        return

    if intent == "courses":
        send_whatsapp_message(sender, "קורסים והשתלמויות:\nיש לנו קורסים דיגיטליים ופרונטליים. רוצה לקבל פירוט? כתוב 'דיגיטליים' או 'פרונטליים'.")
        state["mode"] = "courses"
        return

    if intent == "orders":
        send_whatsapp_message(sender, "הזמנות ומשלוחים:\nלבדיקת מצב הזמנה אנא שלח מספר הזמנה או כתוב 'מעקב'.")
        state["mode"] = "orders"
        return

    if intent == "damaged":
        send_whatsapp_message(sender, "קיבלתי הזמנה פגומה:\nבבקשה שלח את מספר ההזמנה, תיאור התקלה ואם אפשר — תמונה של המוצר.")
        state["mode"] = "damaged"
        return

    if intent == "warranty":
        send_whatsapp_message(sender, "אחריות ותיקונים:\nעל איזה מוצר מדובר ומה הבעיה? בנוסף, כתוב בערך מתי הרכשת את המוצר.")
        state["mode"] = "warranty"
        return

    if message.strip().lower() in ("כן", "כן בבקשה", "חזור", "חזרה", "menu"):
        send_whatsapp_message(sender, MAIN_MENU_TEXT)
        state["mode"] = None
        state["step"] = 1
        return

    # מצבים לפי mode
    if state.get("mode") == "orders":
        digits = ''.join(filter(str.isdigit, message))
        if digits:
            send_whatsapp_message(sender, f"בדקתי את מספר ההזמנה {digits} — סטטוס: במשלוח. צפוי להגעה בעוד 2 ימי עסקים.")
            send_whatsapp_message(sender, "האם תרצה עוד עזרה? (חזור לתפריט / סיום)")
            state["mode"] = None
            return
        else:
            send_whatsapp_message(sender, "לא זיהיתי מספר הזמנה. שלח בבקשה את מספר ההזמנה (רק ספרות).")
            return

    if state.get("mode") == "courses":
        if "דיגיטל" in message:
            send_whatsapp_message(sender, "קורסים דיגיטליים:\n1) קורס בסיסי\n2) קורס מתקדם\nרוצה שנרשום אותך או לשלוח פרטים נוספים? שלח שם ומספר.")
            state["mode"] = None
            return
        if "פרונט" in message:
            send_whatsapp_message(sender, "קורסים פרונטליים:\nהתאריכים הקרובים: 10.01.2026, 24.01.2026\nלרישום שלח שם ומספר.")
            state["mode"] = None
            return
        send_whatsapp_message(sender, "מה סוג הקורס שמעניין אותך? (דיגיטליים / פרונטליים)")
        return

    if state.get("mode") == "damaged":
        digits = ''.join(filter(str.isdigit, message))
        if digits:
            send_whatsapp_message(sender, "תודה. שלחת מספר הזמנה. עכשיו אנא שלח תיאור קצר של הפגם ואם אפשר - תמונה.")
            state["answers"]["order_number"] = digits
            return
        else:
            send_whatsapp_message(sender, "לא זיהיתי מספר הזמנה. שלח בבקשה את מספר ההזמנה (רק ספרות).")
            return

    if state.get("mode") == "warranty":
        send_whatsapp_message(sender, "קיבלתי את פרטיך. נשלח לנציג לבדיקה ונחזור אליך בהקדם. האם תרצה לחזור לתפריט הראשי? (כן/לא)")
        state["mode"] = None
        return

    # ברירת מחדל
    send_whatsapp_message(sender, "אני לא בטוח שהבנתי — הנה התפריט הראשי שוב:")
    send_whatsapp_message(sender, MAIN_MENU_TEXT)
    state["mode"] = None
    state["step"] = 1

# =========================
# פונקציות עזר נוספות
# =========================
def extract_numbers(text):
    return ''.join(filter(str.isdigit, str(text)))

# =========================
# Webhook UltraMsg - גרסה מתוקנת
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data or "data" not in data:
        return jsonify({"status": "error", "message": "No valid JSON received"}), 400

    raw_sender = data["data"]["from"]
    message_body = data["data"]["body"]

    # בדיקה אם ההודעה נשלחה על ידי הבוט עצמו
    is_from_me = data["data"].get("fromMe", False)
    if is_from_me:
        print(f"Skipping message (fromMe=True): {message_body}")
        return jsonify({"status": "ignored_me"}), 200

    sender_digits = extract_numbers(raw_sender)
    bot_digits = extract_numbers(BOT_NUMBER)

    if sender_digits == bot_digits:
        print(f"Ignored message from bot itself (Phone Match).")
        return jsonify({"status": "ignored_self"}), 200

    print(f"Incoming from {sender_digits}: {message_body}")

    handle_message(sender_digits, message_body)
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
