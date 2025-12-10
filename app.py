from flask import Flask, request, jsonify
import requests
import os

# --- 1. הגדרת משתני סביבה לאבטחה ---
# נתונים רגישים נטענים ממשתני סביבה (Environment Variables)
# זה מחייב אותך להגדיר אותם לפני הרצת הקוד (למשל, בקובץ .env)
INSTANCE_ID = os.environ.get("ULTRAMSG_INSTANCE_ID")
TOKEN = os.environ.get("ULTRAMSG_TOKEN")

# בדיקה בסיסית לוודא שהפרטים הרגישים נטענו
if not INSTANCE_ID or not TOKEN:
    print("FATAL: UltraMsg INSTANCE_ID or TOKEN is missing from environment variables.")
    # יציאה מוקדמת אם אין פרטי API
    exit(1)

# כתובת ה-API הבסיסית
ULTRAMSG_API_URL = "https://api.ultramsg.com"

app = Flask(__name__)

# ----------------------------------------------------
# 2. פונקציית שליחה משופרת באמצעות 'requests'
# ----------------------------------------------------
def send_whatsapp_message(to_number: str, message_text: str) -> requests.Response:
    """
    שולחת הודעת WhatsApp דרך UltraMsg API, תוך שימוש בספריית requests.
    """
    # יצירת ה-URL המלא לשליחה
    url = f"{ULTRAMSG_API_URL}/{INSTANCE_ID}/messages/chat"
    
    # בניית הפרמטרים
    params = {
        "token": TOKEN,
        "to": to_number,
        "body": message_text
    }
    
    try:
        # שליחת בקשת POST. ספריית requests מטפלת אוטומטית ב-SSL בצורה בטוחה.
        response = requests.post(url, data=params, timeout=10)
        # זורק חריגה אם הסטטוס קוד הוא 4xx או 5xx
        response.raise_for_status() 
        return response
    
    except requests.exceptions.RequestException as e:
        # טיפול בשגיאות רשת, DNS, חיבור שנכשל, או Timeouts
        print(f"Error sending WhatsApp message: {e}")
        # מחזיר אובייקט תגובה מזויף במקרה של כשל קריטי
        return None

# ----------------------------------------------------
# 3. נקודת הקצה של ה-Webhook עם טיפול משופר
# ----------------------------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    """
    מקבל הודעות נכנסות מה-Webhook של UltraMsg ומגיב אוטומטית.
    """
    try:
        data = request.get_json()
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return "Invalid JSON format", 400

    if not data or "message" not in data:
        # הודעה לא תקינה או חסרת נתונים
        return jsonify({"status": "error", "message": "Invalid request body"}), 400

    msg = data["message"]
    sender = msg.get("from")
    body = msg.get("body")

    if sender and body:
        # *** טיפול בפורמט המספר (נורמליזציה בסיסית - לוודא שהוא מתאים ל-API) ***
        # UltraMsg דורשת פורמט בינלאומי ללא סימנים (+), נניח שה"from" מגיע כבר נקי.
        
        reply_text = f"שלום! קיבלתי את ההודעה שלך: {body} (בוצע שימוש בקוד משופר!)"
        
        response = send_whatsapp_message(sender, reply_text)
        
        if response and response.ok:
            # אם התגובה נשלחה בהצלחה (קוד 2xx)
            return jsonify({"status": "success", "reply_status": response.json()}), 200
        else:
            # אם השליחה נכשלה לאחר ניסיון ה-API
            return jsonify({"status": "error", "message": "Failed to send reply via UltraMsg"}), 500

    return jsonify({"status": "error", "message": "Invalid message format or missing sender/body"}), 400

# ----------------------------------------------------
# 4. הרצת השרת
# ----------------------------------------------------
if __name__ == "__main__":
    # שימוש בפורט מהסביבה (סטנדרטי לאחסון ענן כמו Render)
    port = int(os.environ.get("PORT", 5000))
    # הפעלת השרת
    app.run(host="0.0.0.0", port=port)
