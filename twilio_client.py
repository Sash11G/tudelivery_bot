from twilio.rest import Client
from config import Config

client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

def send_whatsapp_template_message(to, from_, body):
    try:
        message = client.messages.create(
            from_=from_,
            to=to,
            body=body
        )
        print(f"Message sent successfully! Message SID: {message.sid}")
    except Exception as e:
        print(f"Error sending message: {e}")
