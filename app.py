from flask import Flask, request, jsonify
import http.client
import urllib.parse
import ssl

app = Flask(__name__)

# UltraMsg instance details
INSTANCE_ID = "instance155419"
TOKEN = "3y3jgb9grlw0aa6a"

def send_whatsapp_message(to_number, message_text):
    """
    פונקציה ששולחת הודעת WhatsApp דרך UltraMsg API
    """
    conn = http.client.HTTPSConnection("api.ultramsg.com", context=ssl._create_unverified_context())
    
    params = {
        "token": TOKEN,
        "to": to_number,
        "body": message_text
    }
    
    payload = urllib.parse.urlencode(params)
    headers = { "content-type": "application/x-www-form-urlencoded" }
    
    conn.request("POST", f"/{INSTANCE_ID}/messages/chat", payload, headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    return data.decode("utf-8")

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    מקבל הודעות מה‑Webhook של UltraMsg
    """
    data = request.get_json()
    if not data or "message" not in data:
        return "Invalid request", 400

    msg = data["message"]
    sender = msg.get("from")
    body = msg.get("body")

    if sender and body:
        # כאן אפשר לשנות את התגובה
        reply_text = f"שלום! קיבלתי את ההודעה שלך: {body}"
        send_whatsapp_message(sender, reply_text)
        return jsonify({"status": "success"}), 200

    return "Invalid message format", 400

if __name__ == "__main__":
    # Render דורש שימוש ב-port מהסביבה
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
