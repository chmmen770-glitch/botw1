from flask import Flask, request, jsonify
import http.client
import urllib.parse
import ssl

app = Flask(__name__)

# =========================
# הגדרות UltraMsg
# =========================
ULTRAMSG_INSTANCE_ID = "instance155419"
ULTRAMSG_TOKEN = "3y3jgb9grlw0aa6a"

# =========================
# נרמול מספר טלפון
# =========================
def normalize_phone(phone):
    return ''.join(filter(str.isdigit, phone))

# =========================
# שליחת הודעה
# =========================
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
        conn.request("POST", f"/{ULTRAMSG_INSTANCE_ID}/messages/chat", payload, {
            "content-type": "application/x-www-form-urlencoded"
        })
        res = conn.getresponse()
        data = res.read()
        conn.close()

        print("ULTRAMSG RESPONSE:", data.decode("utf-8"))  # <<< לוג חשוב
        return data.decode("utf-8")
    
    except Exception as e:
        print("Error sending message:", e)
        return None

# =========================
# Webhook
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True, silent=True)
        
        print("======================================")
        print("🚨 RECEIVED WEBHOOK DATA:")
        print(data)
        print("======================================")

        if not data:
            return jsonify({"status": "error", "msg": "no json"}), 400

        # כאן אנחנו עדיין לא יודעים מה השדות הנכונים!
        # נחכה לראות מה מגיע בלוגים.

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Webhook error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
