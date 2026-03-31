from flask import Flask, request, jsonify
import requests
import json
import os
import re
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

def extract_info(transcript, summary, customer_phone):
    name = ""
    phone = customer_phone or ""
    address = ""
    service = ""
    date = ""
    time_slot = ""

    if summary:
        name_match = re.search(r'for ([A-Z][a-z]+ [A-Z][a-z]+)', summary)
        if name_match:
            name = name_match.group(1)

        address_match = re.search(r'at ([\d]+ .+?(?:Drive|Street|Ave|Blvd|Road|Dr|St|Ln|Lane|Way|Ct|Court)[,\s]+\w+[\w\s]+\d{5})', summary, re.IGNORECASE)
        if address_match:
            address = address_match.group(1)

        date_match = re.search(r'((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),? ?(?:January|February|March|April|May|June|July|August|September|October|November|December) \d+(?:st|nd|rd|th)?)', summary)
        if date_match:
            date = date_match.group(1)

        time_match = re.search(r'between (\d+(?::\d+)? ?(?:AM|PM) and \d+(?::\d+)? ?(?:AM|PM))', summary)
        if time_match:
            time_slot = time_match.group(1)

    if transcript:
        service_keywords = [
            ("dryer vent", "Dryer Vent Cleaning"),
            ("air duct", "Air Duct Cleaning"),
            ("chimney", "Chimney Sweep"),
            ("inspection", "Free Inspection")
        ]
        for kw, label in service_keywords:
            if kw.lower() in transcript.lower():
                service = label
                break

    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")

    message = f"""Duct Purify - 00276

Customer: {name}
Phone: {phone}
Address: {address}
Service: {service}
Price: $0
Parts: $0
Tip: $0
Payment: 
Date: {date if date else date_str}
Time: {time_slot}
Notes:"""

    return message

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print(f"Received: {json.dumps(data, indent=2)}")

        if data.get("message", {}).get("type") == "end-of-call-report":
            msg = data.get("message", {})
            transcript = msg.get("transcript", "")
            summary = msg.get("analysis", {}).get("summary", "")
            customer_phone = msg.get("customer", {}).get("number", "")
            message = extract_info(transcript, summary, customer_phone)
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
