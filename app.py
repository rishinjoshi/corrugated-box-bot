from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

# ==============================
# ENVIRONMENT VARIABLES
# ==============================
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# ==============================
# IN-MEMORY SESSION STORE
# ==============================
sessions = {}

# ==============================
# WEBHOOK ENDPOINT
# ==============================
@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    # --------------------------------
    # WEBHOOK VERIFICATION (META)
    # --------------------------------
    if request.method == "GET":
        print("🔎 Webhook verification request received")
        print("Query Params:", request.args)
        print("ENV VERIFY_TOKEN:", VERIFY_TOKEN)

        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ Webhook verified successfully")
            return challenge, 200
        else:
            print("❌ Webhook verification failed")
            return "Forbidden", 403

    # --------------------------------
    # INCOMING WHATSAPP MESSAGES
    # --------------------------------
    if request.method == "POST":
        data = request.get_json()
        print("📩 Incoming webhook payload:")
        print(json.dumps(data, indent=2))

        try:
            entry = data["entry"][0]
            change = entry["changes"][0]
            value = change["value"]

            messages = value.get("messages")

            if not messages:
                print("ℹ️ No messages in webhook")
                return "EVENT_RECEIVED", 200

            message = messages[0]
            phone = message["from"]
            text = message["text"]["body"]

            print(f"📞 From: {phone}")
            print(f"💬 Text: {text}")

            if phone not in sessions:
                sessions[phone] = {
                    "step": "START",
                    "data": {}
                }

            reply = handle_message(phone, text)
            send_whatsapp_message(phone, reply)

        except Exception as e:
            print("❌ Error processing webhook:", str(e))

        return "EVENT_RECEIVED", 200


# ==============================
# BOT LOGIC
# ==============================
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
        return "❌ Invalid option.\nReply with 1 to continue."

    if session["step"] == "LENGTH":
        if text.isdigit():
            session["data"]["length"] = int(text)
            session["step"] = "WIDTH"
            return "📐 Enter Box WIDTH (in mm):"
        return "❌ Please enter numeric LENGTH."

    if session["step"] == "WIDTH":
        if text.isdigit():
            session["data"]["width"] = int(text)
            session["step"] = "HEIGHT"
            return "📦 Enter Box HEIGHT (in mm):"
        return "❌ Please enter numeric WIDTH."

    if session["step"] == "HEIGHT":
        if text.isdigit():
            session["data"]["height"] = int(text)
            session["step"] = "PLY"
            return "🧱 Select PLY:\n3️⃣ 3 Ply\n5️⃣ 5 Ply\n7️⃣ 7 Ply"
        return "❌ Please enter numeric HEIGHT."

    if session["step"] == "PLY":
        if text in ["3", "5", "7"]:
            session["data"]["ply"] = text
            session["step"] = "DONE"

            data = session["data"]
            return (
                "✅ Box Details Received:\n\n"
                f"📦 Type: {data['box_type']}\n"
                f"📏 Length: {data['length']} mm\n"
                f"📐 Width: {data['width']} mm\n"
                f"📦 Height: {data['height']} mm\n"
                f"🧱 Ply: {data['ply']}\n\n"
                "Thank you! 🙌"
            )
        return "❌ Invalid ply.\nReply with 3, 5, or 7."

    return "⚠️ Something went wrong.\nType Hi to restart."


# ==============================
# SEND WHATSAPP MESSAGE
# ==============================
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
    print("📤 WhatsApp API response:", response.text)


# ==============================
# HEALTH CHECK
# ==============================
@app.route("/")
def home():
    return "✅ Corrugated Box Bot is LIVE", 200
