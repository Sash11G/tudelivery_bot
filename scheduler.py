from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from twilio_client import send_whatsapp_template_message
from config import Config
import pytz

app = Flask(__name__)
uruguay_tz = pytz.timezone('America/Montevideo')
scheduler = BackgroundScheduler(timezone=uruguay_tz)

def scheduled_send_reminder():
    with app.app_context():
        reminder_message = f"Hola {Config.YOUR_WHATSAPP_NUMBER[9:]}, soy tu asistente virtual de TuDelivery. Deseas ver la lista de productos? Si/No"
        send_whatsapp_template_message(Config.YOUR_WHATSAPP_NUMBER, Config.TWILIO_WHATSAPP_NUMBER, reminder_message)

scheduler.add_job(scheduled_send_reminder, 'cron', day_of_week='wed', hour=13, minute=46)
