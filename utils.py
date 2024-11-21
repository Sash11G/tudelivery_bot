import json
from twilio_client import send_whatsapp_template_message
from openai_client import menu_response, interpret_showing_products, interpret_disengage, update_order_with_ai, tracking_order_response
from config import Config
from functions import format_product_list

user_sessions = {}

def calculate_total_price(order_details):
    total = 0
    for product, quantity in order_details.items():
        total += get_price(product) * quantity
    return total

def get_price(product):
    pass

def initialize_session(phone_number):
    """Initialize a session for a new user."""
    user_sessions[phone_number] = {
        "state": "MAIN_MENU",  # Tracks user status in the flow
        "order_details": {},  # Stores ordered items (product: quantity)
        "conversation_history": [],  # Tracks the conversation thread
        "greeted": False  # Ensures greeting message is shown only once
    }
        
def handle_user_interaction(phone_number, message):
    # Ensure user session exists
    if phone_number not in user_sessions:
        initialize_session(phone_number)

    session = user_sessions[phone_number]
    state = session['state']
    order_details = session['order_details']
    greeted = session['greeted']
    
    # Add the user's message to the conversation history
    session["conversation_history"].append({"role": "user", "content": message})

    # Main menu logic
    if state == 'MAIN_MENU':
        if not greeted:
            # Show greeting only once
            greeting_message = (
                "Hola! Soy tu asistente virtual de TuDelivery. Bienvenido.\n\n"
                "Menú Interactivo:\n\n"
                "1. Ver lista de productos\n"
                "2. Hacer pedido\n"
                "3. Finalizar"
            )
            session['greeted'] = True
        else:
            # Only show menu without greeting
            greeting_message = (
                "Menú Interactivo:\n\n"
                "1. Ver lista de productos\n"
                "2. Hacer pedido\n"
                "3. Finalizar"
            )
        send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, greeting_message)
        session['state'] = 'AWAITING_MAIN_MENU_CHOICE'

    elif state == 'AWAITING_MAIN_MENU_CHOICE':
        print("\nAwaiting menu choice\n\n")
        intent = menu_response(message)  # Use updated logic to interpret message
        print(f"intent= {intent}\n\n")
        if intent == 'view_products':
            session['state'] = 'SHOWING_PRODUCTS'
            product_list_message = f"{format_product_list()}\n\nOpciones:\n1. Hacer pedido\n2. Volver al menú principal."
            send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, product_list_message)
        elif intent == 'make_order':
            session['state'] = 'TRACKING_ORDER'
            order_prompt_message = "Por favor, ingrese el producto y la cantidad que desea ordenar (e.g., '2 Pollo Supremas')."
            send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, order_prompt_message)
        elif intent == 'finish':
            polite_disengagement_message = "Entendido. ¿Hay algo más en lo que pueda ayudarte? Si no, que tengas un buen día."
            send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, polite_disengagement_message)
            session['state'] = 'DISENGAGED'
        elif intent == 'greet':
            # Redirect to main menu without greeting again
            session['state'] = 'MAIN_MENU'
            handle_user_interaction(phone_number, None)
        else:
            error_message = "No entendí tu respuesta. Por favor Men válida: 1, 2 o 3."
            send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, error_message)

    elif state == 'SHOWING_PRODUCTS':
        intent = interpret_showing_products(message)  # Use the new function for this state

        if intent == 'order':
            try:
                # Update the order using AI
                session["order_details"] = update_order_with_ai(message, session.get("order_details", {}))

                # Generate a user-friendly formatted message
                order_summary = "\n".join(
                    [f"{product}{f' x{details['quantity']}'} TOTAL: $ {details['price']}"
                    for product, details in session["order_details"].items()]
                )

                # Calculate the total cost
                total_cost = sum(details['price'] for details in session["order_details"].values())

                # Generate the confirmation message
                confirm_message = (
                    "Tu pedido ha sido actualizado:\n\n"
                    f"{order_summary}\n\n"
                    f"COSTO TOTAL: $ {total_cost}\n\n"
                    "Escribe más productos para continuar agregando.\n\n"
                    "Menu:\n"
                    "1. Confirmar Pedido.\n"
                    "2. Volver a Menu Principal.\n"
                )
                send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, confirm_message)
                session['state'] = 'TRACKING_ORDER'
            except ValueError as e:
                send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, str(e))


        elif intent == 'make_order':
            session['state'] = 'TRACKING_ORDER'
            order_prompt_message = "Por favor, ingrese el producto y la cantidad que desea ordenar (e.g., '2 Pollo Supremas')."
            send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, order_prompt_message)
        elif intent == 'main_menu':
            session['state'] = 'MAIN_MENU'
            handle_user_interaction(phone_number, None)
        else:  # 'invalid' or unrecognized intent
            error_message = (
                "No entendí tu respuesta. Selecciona:\n"
                "1. Hacer pedido\n"
                "2. Volver al menú principal\n"
                "O ingresa un pedido directamente en el formato '2 kg Supremas'."
            )
            send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, error_message)


    elif state == "TRACKING_ORDER":
        
        user_intent = tracking_order_response(message)
        if user_intent == "add_products":
            try:
                # Update the order using AI
                session["order_details"] = update_order_with_ai(message, session.get("order_details", {}))

                # Generate a user-friendly formatted message
                order_summary = "\n".join(
                    [f"{product}{f' x{details['quantity']}'} TOTAL: $ {details['price']}"
                    for product, details in session["order_details"].items()]
                )
                
                # Debugging: Print the order summary for verification
                print("DEBUG: Order Summary for Message:", order_summary)
                print("\n\n")
                print("DEBUG: Current order_details:", session["order_details"])

                
                # Calculate the total cost
                total_cost = sum(details['price'] for details in session["order_details"].values())

                # Generate the confirmation message
                confirm_message = (
                    "Tu pedido ha sido actualizado:\n\n"
                    f"{order_summary}\n\n"
                    f"COSTO TOTAL: $ {total_cost}\n\n"
                    "Escribe más productos para continuar agregando.\n\n"
                    "Menu:\n"
                    "1. Confirmar Pedido.\n"
                    "2. Volver a Menu Principal.\n"
                )

                send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, confirm_message)

            except ValueError as e:
                send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, str(e))
                
        elif user_intent == "confirm_order":
            # Confirm the order
            order_summary = "\n".join(
                [f"{product} x{details['quantity']} TOTAL: ${details['quantity'] * details['price']}"
                for product, details in session["order_details"].items()]
            )
            total_cost = sum(details['quantity'] * details['price'] for details in session["order_details"].values())
            
            confirmation_message = (
                "¡Pedido confirmado!\n\n"
                "Este es tu pedido:\n"
                f"{order_summary}\n\n"
                f"Total: ${total_cost}\n\n"
                f"Tu pedido fue confirmado para el número {phone_number}.\n"
                "Un operador se pondrá en contacto contigo en breve.\n"
                "¿Hay algo más en lo que pueda ayudarte? Si no, que tengas un buen día."
            )
            
            # Send confirmation message
            send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, confirmation_message)

            # Update state to DISENGAGED
            session["state"] = "DISENGAGED"
            
        elif user_intent == "main_menu":
            # Return to main menu
            session["order_details"] = {}  # Clear the order list
            session["state"] = "MAIN_MENU"
            handle_user_interaction(phone_number, None)

        else:
            # Unrecognized intent
            send_whatsapp_template_message(
                phone_number,
                Config.TWILIO_WHATSAPP_NUMBER,
                "No entendí tu respuesta. Por favor, selecciona una opción válida."
            )


    elif state == 'DISENGAGED':
        intent = interpret_disengage(message)
        if intent == 'greet':
            session['state'] = 'MAIN_MENU'
            handle_user_interaction(phone_number, None)
        else:
            polite_disengagement_message = "¡Gracias por usar TuDelivery! Que tengas un excelente día."
            send_whatsapp_template_message(phone_number, Config.TWILIO_WHATSAPP_NUMBER, polite_disengagement_message)
            session['state'] = 'MAIN_MENU'
            session['greeted'] = False
            
            
            
            

        
