from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # Meta webhook verification
    challenge = request.args.get("hub.challenge")
    if challenge:
        return challenge, 200

    # Incoming WhatsApp messages (later use)
    data = request.get_json()
    print(data)
    return "EVENT_RECEIVED", 200

@app.route("/")
def home():
    return "Webhook is live", 200
