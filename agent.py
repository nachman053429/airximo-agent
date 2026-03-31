from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

GREEN_API_URL = "https://7107.api.greenapi.com"
INSTANCE_ID = "7107569796"
INSTANCE_TOKEN = "c5364f36516647d0b7a48a6652d3278e73916bc9020e40298d"
GROUP_ID = "120363409953665712@g.us"

def send_whatsapp(message):
    url = f"{GREEN_API_URL}/waInstance{INSTANCE_ID}/sendMessage/{INSTANCE_TOKEN}"
    payload = {
        "chatId": GROUP_ID,
        "message": message
    }
    response = requests.post(url, json=payload)
    return response.json()

def format_job(data):
    customer_name = data.get("customer", {}).get("name", "")
    phone = data.get("customer", {}).get("number", "")
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")

    message = f"""Duct Purify - 00276

Customer: {customer_name}
Phone: {phone}
Address: 
Service: 
Price: $0
Parts: $0
Tip: $0
Payment: 
Date: {date_str}
Time: 
Notes:"""

    return message

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print(f"Received: {json.dumps(data, indent=2)}")
        
        if data.get("message", {}).get("type") == "end-of-call-report":
            message = format_job(data.get("message", {}))
            result = send_whatsapp(message)
            print(f"WhatsApp sent: {result}")
            
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Airximo Agent Started!")
    print("📞 Waiting for calls...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
