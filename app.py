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

@app.route("/webhook", methods=["POST"])
def webhook():

    print("======================================")
    print("🚨 NEW WEBHOOK CALL RECEIVED")

    print("\n🔹 request.headers:")
    print(dict(request.headers))

    print("\n🔹 request.form:")
    print(request.form)

    print("\n🔹 request.args:")
    print(request.args)

    print("\n🔹 request.data (raw body):")
    print(request.data)

    print("\n🔹 request.json:")
    print(request.get_json(silent=True))
    print("======================================\n")

    return jsonify({"status": "ok"}), 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
