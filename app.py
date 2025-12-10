from flask import Flask, request, jsonify
import http.client
import urllib.parse
import ssl

app = Flask(__name__)

# =========================
# הגדרות UltraMsg
# =========================
ULTRAMSG_INSTANCE_ID = "instance155419"  # ה-Instance שלך
ULTRAMSG_TOKEN = "3y3jgb9grlw0aa6a"     # ה-Token שלך

# =========================
# פונקציה לנרמול מספר טלפון
# =========================
def normalize_phone(phone):
    # מסיר +, רווחים ומקפים
    return ''.join(filter(str.isdigit, phone))

# =========================
# פונקציה לשליחת הודעת WhatsApp
# =========================
def send_whatsapp_message(to, message):
    try:
        # נרמול מספר
        to_normalized = normalize_phone(to)

        params = {
            "token": ULTRAMSG_TOKEN,
            "to": to_normalized,
            "body": message
        }
        payload = urllib.parse.urlencode(params)
        
        conn = http.client.HTTPSConnection("api.ultramsg.com", context=ssl._create_unverified_context())
        conn.request("POST", f"/{ULTRAMSG_INSTANCE_ID}/messages/chat", payload, {"content-type": "application/x-www-form-urlencoded"})
        res = conn.getresponse()
        data = res.read()
        conn.close()
        
        return data.decode("utf-8")
    
    except Exception as e:
        print("Error sending message:", e)
        return None

# =========================
# Webhook של UltraMsg
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON received"}), 400

        # בודק אם יש הודעה נכנסת
        if "body" in data and "from" in data:
            sender = data["from"]
            message = data["body"]
            print(f"Received message from {sender}: {message}")

            # שליחת תגובה אוטומטית
            response_text = f"תודה! קיבלנו את ההודעה שלך: {message}"
            send_whatsapp_message(sender, response_text)
        
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Webhook error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

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
