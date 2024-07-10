from twilio_client import send_whatsapp_template_message
from openai_client import interpret_response
from config import Config

product_list = {
    "Origen Animal": {
        "Pollo Supremas - 1 kg": 400,
        "Huevos (orgánicos, comunes) - 12 unidades": 200,
        "Milanesas - 1 kg": 560,
    },
    "Granos y Cereales": {
        "Granola - 500 g": 320,
        "Quinoa - 500 g": 400,
        "Arroz - 1 kg": 160,
        "Arroz integral - 1 kg": 240,
        "Avena - 1 kg": 192,
    },
    "Frutas y Verduras": {
        "Bananas - 1 kg": 128,
        "Paltas - 1 unidad": 80,
        "Papas - 1 kg": 64,
        "Boniatos - 1 kg": 80,
    },
    "Frutos Secos y Semillas": {
        "Nueces - 200 g": 240,
        "Almendras - 200 g": 288,
        "Castañas de cajú - 200 g": 320,
    },
    "Legumbres": {
        "Porotos negros - 500 g": 128,
        "Porotos manteca - 500 g": 144,
        "Garbanzo - 500 g": 160,
        "Lentejas - 500 g": 112,
    },
    "Aceites": {
        "Aceite de oliva - 500 ml": 480,
    },
    "Otros": {
        "Alimento mascota - 3 kg": 960,
    }
}

def format_product_list(product_list):
    formatted_list = "Lista de productos disponibles:\n\n"
    for category, items in product_list.items():
        formatted_list += f"{category}:\n"
        for product, price in items.items():
            formatted_list += f"- {product}: ${price}\n"
        formatted_list += "\n"
    return formatted_list

def handle_user_interaction(phone_number, response):
    if interpret_response(response):
        print('2')
        product_list_message = format_product_list(product_list)
        send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, product_list_message)
    else:
        polite_disengagement_message = "Entendido. ¿Hay algo más en lo que pueda ayudarte? Si no, que tengas un buen día."
        send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, polite_disengagement_message)
