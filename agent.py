from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# ═══════════════════════════════════════
# הגדרות - GREEN API
# ═══════════════════════════════════════
GREEN_API_URL = "https://7107.api.greenapi.com"
INSTANCE_ID = "7107569796"
INSTANCE_TOKEN = "c5364f36516647d0b7a48a6652d3278e73916bc9020e40298d"
GROUP_ID = "120363409953665712@g.us"

# ═══════════════════════════════════════
# פונקציה לשליחת הודעה לוואטסאפ
# ═══════════════════════════════════════
def send_whatsapp(message):
    url = f"{GREEN_API_URL}/waInstance{INSTANCE_ID}/sendMessage/{INSTANCE_TOKEN}"
    payload = {
        "chatId": GROUP_ID,
        "message": message
    }
    response = requests.post(url, json=payload)
    return response.json()

# ═══════════════════════════════════════
# פונקציה לעיבוד נתוני השיחה
# ═══════════════════════════════════════
def format_job(data):
    transcript = data.get("transcript", "")
    customer_name = data.get("customer", {}).get("name", "Unknown")
    phone = data.get("customer", {}).get("number", "Unknown")
    
    message = f"""🏠 *Airximo - New Job*
━━━━━━━━━━━━━━━━━━━━
👤 *Customer:* {customer_name}
📞 *Phone:* {phone}
━━━━━━━━━━━━━━━━━━━━
📋 *Transcript Summary:*
{transcript[:500] if transcript else "No transcript available"}
━━━━━━━━━━━━━━━━━━━━
🤖 _Sent by Airximo AI Agent_"""
    
    return message

# ═══════════════════════════════════════
# Webhook - מקבל נתונים מ-VAPI
# ═══════════════════════════════════════
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print(f"Received: {json.dumps(data, indent=2)}")
        
        # בדוק שהשיחה הסתיימה
        if data.get("message", {}).get("type") == "end-of-call-report":
            message = format_job(data.get("message", {}))
            result = send_whatsapp(message)
            print(f"WhatsApp sent: {result}")
            
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════
# הרצת השרת
# ═══════════════════════════════════════
if __name__ == '__main__':
    print("🚀 Airximo Agent Started!")
    print("📞 Waiting for calls...")
    app.run(host='0.0.0.0', port=5000, debug=True)
