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
        "Bonjour et bienvenue chez Beauty Studio 💅\n"
        "Comment puis-je vous aider ? 🌸\n\n"
        "1️⃣ 📦 Commandes et livraisons\n"
        "2️⃣ 🛠️ Garantie / réparation / produit défectueux\n\n"
        "Écrivez un numéro ou *menu* 💕"
    )

# ================= LOGIC =================
def handle_message(sender, text, media_link=""):
    text_clean = text.lower().strip()

    if sender not in user_states:
        user_states[sender] = {"stage": "menu"}
        send_main_menu(sender)
        return

    if text_clean == "menu":
        user_states[sender] = {"stage": "menu"}
        send_main_menu(sender)
        return

    stage = user_states[sender]["stage"]

    # ===== MENU =====
    if stage == "menu":

        if text_clean in ["1", "commandes", "livraisons", "commandes et livraisons"]:
            user_states[sender]["stage"] = "orders_menu"
            send_message(
                sender,
                "📦 Commandes et livraisons\n"
                "Que souhaitez-vous savoir ?\n"
                "🚚 Délais et frais de livraison\n"
                "📦 Suivi de commande\n\n"
                "*menu* pour revenir"
            )

        elif text_clean in ["2", "garantie", "réparation", "défectueux", "défectueuse"]:
            user_states[sender]["stage"] = "warranty"
            send_message(
                sender,
                "Afin de traiter votre demande au mieux 🌸\n"
                "Merci d’envoyer :\n\n"
                "• Nom complet\n"
                "• Numéro de commande (si disponible)\n"
                "• Produit concerné\n"
                "• Description du problème\n"
                "• Photo (si disponible)\n\n"
                "Un récapitulatif vous sera envoyé 💛\n"
                "*menu* pour revenir"
            )

        else:
            send_main_menu(sender)

    # ===== ORDERS MENU =====
    elif stage == "orders_menu":
        if "délai" in text_clean or "livraison" in text_clean:
            send_message(
                sender,
                "🚚 Délais et frais de livraison :\n"
                "Délai de livraison : 3 à 5 jours ouvrables\n"
                "Frais de livraison : 35₪\n\n"
                "*menu*"
            )

        elif "suivi" in text_clean:
            send_message(
                sender,
                "📦 Suivi de commande\n"
                "Merci d’envoyer votre numéro de commande ou votre nom complet\n\n"
                "*menu*"
            )

        else:
            send_message(
                sender,
                "Veuillez choisir :\n"
                "🚚 Délais et frais de livraison\n"
                "📦 Suivi de commande\n\n"
                "*menu*"
            )

    # ===== WARRANTY / REPAIR =====
    elif stage == "warranty":

        summary = (
            "🛠️ Nouvelle demande – Garantie / réparation / produit défectueux\n\n"
            f"📞 Téléphone : {sender}\n\n"
            f"📝 Détails de la cliente :\n{text}"
        )

        if media_link:
            summary += f"\n\n📸 Photo :\n{media_link}"

        send_message(ADMIN_NUMBER, summary)
        send_email("Nouvelle demande – Garantie / réparation", summary)

        # Récapitulatif client
        send_message(
            sender,
            "💛 Récapitulatif de votre demande :\n\n"
            "Type de demande : Garantie / réparation / produit défectueux\n"
            f"Téléphone : {sender}\n"
            f"Détails envoyés :\n{text}\n\n"
            "Votre demande a bien été reçue 🌸\n"
            "Nous vous recontacterons très bientôt 💅\n\n"
            "*menu*"
        )

        user_states[sender] = {"stage": "menu"}

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
