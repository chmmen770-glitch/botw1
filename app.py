from flask import Flask, request, jsonify
import http.client
import urllib.parse
import ssl

app = Flask(__name__)

ULTRAMSG_INSTANCE_ID = "instance155419"
ULTRAMSG_TOKEN = "3y3jgb9grlw0aa6a"

def normalize_phone(phone):
    return ''.join(filter(str.isdigit, phone))

def send_whatsapp_message(to, message):
    try:
        to_normalized = normalize_phone(to)
        params = {
            "token": ULTRAMSG_TOKEN,
            "to": to_normalized,
            "body": message
        }
        payload = urllib.parse.urlencode(params)

        conn = http.client.HTTPSConnection(
            "api.ultramsg.com",
            context=ssl._create_unverified_context()
        )
        conn.request(
            "POST",
            f"/{ULTRAMSG_INSTANCE_ID}/messages/chat",
            payload,
            {"content-type": "application/x-www-form-urlencoded"}
        )
        res = conn.getresponse()
        data = res.read()
        conn.close()

        print("SEND RESPONSE:", data.decode("utf-8"))
        return data.decode("utf-8")

    except Exception as e:
        print("SEND ERROR:", e)
        return None


@app.route("/webhook", methods=["POST"])
def webhook():

    print("\n==================== NEW WEBHOOK ====================\n")

    data = request.get_json(silent=True)

    print("RAW BODY:", request.data)
    print("JSON:", data)

    if not data:
        print("❌ No JSON received.")
        return jsonify({"status": "no json"}), 200

    event_type = data.get("event_type")
    payload = data.get("data", {})

    print("Event type:", event_type)

    # === KEY CHANGE HERE! matches UltraMsg format exactly ===
    if event_type == "message_received":
        msg_from = payload.get("from")
        msg_body = payload.get("body")
        msg_type = payload.get("type")

        print(f"📩 Received message from {msg_from}")
        print(f"Body: {msg_body}")
        print(f"Type: {msg_type}")

        # Example: Auto reply ONLY to private chat messages
        if not payload.get("fromMe"):
            number = msg_from.replace("@c.us", "")
            send_whatsapp_message(number, f"נלקח: {msg_body}")

    print("\n=====================================================\n")

    return jsonify({"status": "ok"}), 200


@app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
