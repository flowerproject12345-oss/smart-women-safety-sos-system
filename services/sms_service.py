"""
📱 SMS Service - Send SMS alerts
"""

import requests
from config import Config
from datetime import datetime   # ✅ FIX: missing import


def send_sms_alert(phone_number, user_name, latitude, longitude, address):
    """Send SMS alert to emergency contact"""

    # ✅ DEMO MODE (no real SMS)
    if Config.DEMO_MODE:
        print(f"📱 [DEMO] SMS to: {phone_number}")
        print(f"🚨 SOS from {user_name}")
        print(f"Location: {address}")
        print(f"Maps: https://maps.google.com/?q={latitude},{longitude}")
        return True

    # ✅ TWILIO (REAL SMS)
    try:
        from twilio.rest import Client

        client = Client(
            Config.TWILIO_ACCOUNT_SID,
            Config.TWILIO_AUTH_TOKEN
        )

        google_maps_link = f"https://maps.google.com/?q={latitude},{longitude}"

        message = f"""🚨 EMERGENCY SOS ALERT 🚨

{user_name} has triggered an SOS alert!

📍 Location: {address}
🗺️ Maps: {google_maps_link}

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please check immediately!
"""

        client.messages.create(
            body=message,
            from_=Config.TWILIO_PHONE_NUMBER,
            to=phone_number
        )

        return True

    except Exception as e:
        print(f"❌ SMS Error: {e}")
        return False


def send_bulk_sms(contacts, user_name, latitude, longitude, address):
    """Send SMS to multiple contacts"""

    results = []

    for contact in contacts:
        if contact.get('phone'):
            sent = send_sms_alert(
                contact['phone'],
                user_name,
                latitude,
                longitude,
                address
            )

            results.append({
                'contact': contact.get('name', 'Unknown'),
                'phone': contact['phone'],
                'sent': sent
            })

    return results