from flask import Flask, request
import requests
import os

app = Flask(__name__)

# In-memory session store
sessions = {}

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    print("🔥 META WEBHOOK HIT")

    # STEP 1: Verification (GET)
    if request.method == "GET":
        challenge = request.args.get("hub.challenge")
        return challenge, 200

    # STEP 2: Incoming message (POST)
    data = request.get_json()
    print("📦 DATA RECEIVED:", data)

    return "EVENT_RECEIVED", 200


def handle_message(phone, text):
    session = sessions[phone]

    if session["step"] == "START":
        session["step"] = "BOX_TYPE"
        return (
            "👋 Welcome to Corrugated Box Calculator\n\n"
            "Please choose Box Type:\n"
            "1️⃣ Universal Box\n\n"
            "Reply with 1 to continue."
        )

    if session["step"] == "BOX_TYPE":
        if text == "1":
            session["data"]["box_type"] = "Universal"
            session["step"] = "LENGTH"
            return "📏 Enter Box LENGTH (in mm):"
        else:
            return "❌ Invalid option.\nReply with 1 for Universal Box."

    if session["step"] == "LENGTH":
        if text.isdigit():
            session["data"]["length"] = int(text)
            session["step"] = "WIDTH"
            return "📐 Enter Box WIDTH (in mm):"
        else:
            return "❌ Please enter numeric LENGTH in mm."

    if session["step"] == "WIDTH":
        if text.isdigit():
            session["data"]["width"] = int(text)
            session["step"] = "HEIGHT"
            return "📦 Enter Box HEIGHT (in mm):"
        else:
            return "❌ Please enter numeric WIDTH in mm."

    if session["step"] == "HEIGHT":
        if text.isdigit():
            session["data"]["height"] = int(text)
            session["step"] = "PLY"
            return "🧱 Select PLY:\n3️⃣ 3 Ply\n5️⃣ 5 Ply\n7️⃣ 7 Ply"
        else:
            return "❌ Please enter numeric HEIGHT in mm."

    return "⚠️ Something went wrong. Please type Hi to restart."


WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

def send_whatsapp_message(phone, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("WhatsApp send response:", response.text)



@app.route("/")
def home():
    return "Corrugated Box Bot is LIVE", 200
