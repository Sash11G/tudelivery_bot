from flask import Flask, request, jsonify
from config import Config
from twilio_client import send_whatsapp_template_message
from scheduler import scheduler, scheduled_send_reminder
from utils import handle_user_interaction

app = Flask(__name__)
app.config.from_object(Config)

scheduler.start()

@app.route("/send-reminder", methods=["GET"])
def send_reminder_route():
    reminder_message = f"Hola {Config.YOUR_WHATSAPP_NUMBER[9:]}, soy tu asistente virtual de TuDelivery. Deseas ver la lista de productos? Si/No"
    send_whatsapp_template_message(Config.YOUR_WHATSAPP_NUMBER, Config.TWILIO_WHATSAPP_NUMBER, reminder_message)
    return jsonify(success=True)

@app.route("/", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "").strip()

    print(f"Incoming message from {from_number}: \n{incoming_msg}")

    if incoming_msg:
        try:
            print('1')
            handle_user_interaction(from_number, incoming_msg)
        except Exception as e:
            print(f'Error in webhook: {e}')

    return jsonify(success=True)

if __name__ == "__main__":
    app.run(debug=True)
