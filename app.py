from flask import Flask, request

app = Flask(__name__)

# In-memory session store
sessions = {}

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # Meta verification
    challenge = request.args.get("hub.challenge")
    if challenge:
        return challenge, 200

    data = request.get_json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages")

        if not messages:
            return "OK", 200

        msg = messages[0]
        phone = msg["from"]
        text = msg["text"]["body"].strip().lower()

        # Create session if new user
        if phone not in sessions:
            sessions[phone] = {
                "step": "START",
                "data": {}
            }

        # Handle conversation
        reply = handle_message(phone, text)

        send_whatsapp_message(phone, reply)

    except Exception as e:
        print("ERROR:", e)

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


def send_whatsapp_message(phone, message):
    # For now just log (we’ll wire API next)
    print(f"➡️ Send to {phone}: {message}")


@app.route("/")
def home():
    return "Corrugated Box Bot is LIVE", 200
