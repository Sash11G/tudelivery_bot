from flask import Flask
from twilio.rest import Client
from config import Config

app = Flask(__name__)

# Twilio credentials from your Twilio dashboard
account_sid = Config.TWILIO_ACCOUNT_SID
auth_token = Config.TWILIO_AUTH_TOKEN
twilio_whatsapp_number = Config.TWILIO_WHATSAPP_NUMBER  # Default Twilio WhatsApp number
your_whatsapp_number = "whatsapp:+59894455161"   # Replace with your recipient number

# Initialize the Twilio client
client = Client(account_sid, auth_token)

def send_whatsapp_message():
    try:
        message = client.messages.create(
            from_=twilio_whatsapp_number,
            body= f"Hola {your_whatsapp_number[9:]}, soy tu asistente virtual de TuDelivery. Deseas ver la lista de productos? Si/No",
            to=your_whatsapp_number
        )
        print(f"Message sent successfully! SID: {message.sid}")
    except Exception as e:
        print(f"Failed to send message: {e}")

if __name__ == '__main__':
    # Send the WhatsApp message as soon as the script runs
    send_whatsapp_message()

    # Start the Flask app (optional, if you want the app to keep running)
    app.run(debug=False)
