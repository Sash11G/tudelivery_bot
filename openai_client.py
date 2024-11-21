import json
from openai import OpenAI
from config import Config
from functions import get_product_list

openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)

def menu_response(user_response):
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "Your job is to interpret a user message and evaluate its meaning in the context of a menu system with three options. "
                    "The options are:\n\n"
                    "1. 'View products' (user might type 1, 'ver productos', or something similar).\n"
                    "2. 'Make an order' (user might type 2, 'hacer pedido', or similar phrases).\n"
                    "3. 'Finish' (user might type 3, 'finalizar', 'stop', or similar phrases).\n"
                    "4. Random greeting or unrelated message (e.g., 'hi', 'hello', or a random Spanish greeting).\n\n"
                    "Your response should be:\n\n"
                    "view_products" "if the message corresponds to option 1.\n"
                    "make_order" "if the message corresponds to option 2.\n"
                    "finish" "if the message corresponds to option 3.\n"
                    "greet" "for any greeting or unrelated message.\n\n"
                    "Ensure you account for both English and Spanish inputs. Return only the corresponding response in lowercase: "
                    "view_products" "make_order" "finish" "greet" "Do not include any additional explanations."
                )
            },
            {"role": "user", "content": user_response}
        ]
    )
    answer = response.choices[0].message.content.strip().lower()
    return answer

def update_order_with_ai(message, order_list):
    """
    Sends the user input to the AI to update the order and stores the response in order_list.

    Args:
        message (str): User's input message.
        order_list (dict): The current order dictionary to be updated.

    Returns:
        dict: Updated order list.
    """
    # Get the product list for the AI
    raw_product_list = get_product_list()
    flat_product_list = [
        f"{product}: ${price}" for category in raw_product_list.values() for product, price in category.items()
    ]

    # AI prompt
    prompt = f"""
    Lista de Productos Disponibles:
    {', '.join(flat_product_list)}

    Pedido actual:
    {json.dumps(order_list, indent=2) if order_list else 'No hay pedido aún.'}

    Nuevo mensaje del usuario:
    "{message}"

    Tarea:
    1. Analiza el mensaje del usuario y verifica si los productos están disponibles.
    2. Si están disponibles, devuelve un objeto JSON con el formato:
       {{
           "product_name": {{"quantity": int, "price": float}},
           ...
       }}
    3. Si hay un error, devuelve un mensaje explicando el problema.
    """

    try:
        # Mock AI response (Replace with actual OpenAI API call)
        ai_response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente que procesa pedidos de usuarios y devuelve objetos JSON con detalles de pedidos. Solo devuelve el objeto JSON, nada más. En el formato { 'product_name': {'quantity': int, 'price': float}, ...} "},
                {"role": "user", "content": prompt},
            ]
        )

        ai_message = ai_response.choices[0].message.content.strip()
        ai_data = json.loads(ai_message)  # Parse the JSON response from the AI

        # Debugging: Print the raw AI data
        print("DEBUG: AI Response JSON:", ai_data)

        # Merge AI response into the order list
        for product_name, details in ai_data.items():
            if product_name in order_list:
                # Check if quantity and price are unchanged
                existing_details = order_list[product_name]
                if (
                    existing_details["quantity"] == details["quantity"]
                    and existing_details["price"] == details["price"]
                ):
                    # Skip updating if nothing has changed
                    print(f"DEBUG: No change for {product_name}. Skipping update.")
                    continue

                # Update the quantity and price only if they differ
                print(f"DEBUG: Updating {product_name}: {existing_details} -> {details}")
                order_list[product_name]["quantity"] = details["quantity"]
                order_list[product_name]["price"] = details["price"]
            else:
                # Add new product to the order
                print(f"DEBUG: Adding new product {product_name} with details {details}")
                order_list[product_name] = {"quantity": details["quantity"], "price": details["price"]}

        # Debugging: Print the updated order list
        print("DEBUG: Updated Order List:", order_list)

        return order_list

    except json.JSONDecodeError as e:
        print("Error decoding AI response:", e)
        raise ValueError("La respuesta del AI no se pudo procesar. Por favor, intenta nuevamente.")
    except Exception as e:
        print("Unexpected error:", e)
        raise ValueError("Hubo un problema al procesar tu pedido.")


# _______________________ NEW _________________________

# def interpret_order(message):
#     """
#     Interpret the user's order input using AI and validate it against the product list.
#     """
#     prompt = f"""
#     Lista de Productos Disponibles:
#     {get_product_list()}


#     Nuevo mensaje del usuario:
#     "{message}"

#     Tarea:
#     1. Analiza el mensaje del usuario y verifica si los productos están disponibles.
#     2. Si están disponibles, actualiza el pedido con los nuevos productos y cantidades.
#     3. Responde en este formato:
#         Tu pedido ha sido actualizado:\n- [Producto]: [Cantidad]\n Deseas agregar algo mas?
#     4. Si hay un error, envía un mensaje que explique el problema.
#     """

#     # Mock AI response (Replace with actual OpenAI API call)
#     ai_response = openai_client.chat.completions.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": "Eres un asistente que procesa pedidos de usuarios y actualiza sus listas de productos. Responde el mensaje con el formato entre comillas en el punto 3, no agregues mas texto que ese, tu respuesta a este mensaje debe ser solo ese formato, pero sin las comillas."},
#             {"role": "user", "content": prompt},
#         ]
#     )

#     answer = ai_response.choices[0].message.content.strip()
#     return answer


def tracking_order_response(user_response):
    """
    Interpret the user's response in the context of the TRACKING_ORDER menu.

    Args:
        user_response (str): The user's input message.

    Returns:
        str: One of the following responses:
             - "add_products": User wants to add more products.
             - "confirm_order": User wants to confirm their order.
             - "main_menu": User wants to return to the main menu.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant that interprets user responses in the context of a menu system for managing orders.\n\n"
                    "The menu options are:\n"
                    "1. 'Confirm order' (e.g., user types '1', 'confirmar pedido', or something similar).\n"
                    "2. 'Return to main menu' (e.g., user types '2', 'volver a menú principal', or similar phrases).\n"
                    "3. 'Add more products' (e.g., user types anything resembling adding more products or providing product details).\n\n"
                    "Your task is to interpret the user's message and respond with:\n"
                    "confirm_order" "if the user wants to confirm their order.\n"
                    "main_menu" "if the user wants to return to the main menu.\n"
                    "add_products" "if the user wants to add more products or continue ordering.\n\n"
                    "Only respond with one of these exact words:" "confirm_order" "main_menu" "add_products" "Do not include explanations"
                ),
            },
            {"role": "user", "content": user_response},
        ],
    )
    answer = response.choices[0].message.content.strip().lower()
    return answer



# def interpret_order(user_response, current_order):
#     prompt = f"Current order of the user so far is: {current_order} User message: {user_response}. Available-Products-List: {get_product_list}"

#     response = openai_client.chat.completions.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": "You are a Grocery Deliver Assistant, and you have to analyze and parse the user 'current order' and the 'user message', the current order are the items the user has selected so far, the 'user message' are products the user has just chosen. The products from 'user message' might be available or invalid, for that you have to check if they exist in 'Available-Products-List'. In 'Available-Products-List' you will also have the prices for the items, the 'user-message' should provide the product and the quantity, if they dont provide it, then tell the user they should provide both product and quantity (product-quantity pair)."
#              "Based on the user input you will decide the following:"
#              "A) The user provided correct information (available product and quantity)"
#              "B) The user either provided an invalid product not found in 'Available-Products-List' or they didnt provide full information (product-quantity pair)"
#              "Based on this you shall return on of the following commands:"
#              "correct_order" "if the user has provided correct info as mentioned in case A"
#              "invalid_order" "if the user has provided invalid info as mentioned in case B"
#              "You shall only answer with 1 word, no further text, just 1 keyword of these 2:" "correct-order" "invalid_order"},
#             {"role": "user", "content": prompt}
#         ]
#     )

#     updated_order = response.choices[0].message.content.strip()
#     return json.loads(updated_order)




def interpret_showing_products(user_response):
    """
    Interprets user input in the 'SHOWING_PRODUCTS' state.
    Determines if the user wants to place an order, navigate, or return to the main menu.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "Your job is to interpret user input in the context of a product menu system. "
                    "Determine if the user wants to:\n"
                    "1. Place an order directly (e.g., '2 Pollo Supremas').\n"
                    "2. Choose the option 'Make an order' (e.g., type '1' or 'hacer pedido').\n"
                    "3. Return to the main menu (e.g., type '2' or 'volver al menú principal').\n"
                    "4. Any invalid or unrecognized input.\n\n"
                    "Your response should be:\n"
                    "order" "if the user input looks like an order (e.g., '2 Pollo Supremas').\n"
                    "make_order" "if the input corresponds to choosing the option to make an order.\n"
                    "main_menu" "if the user wants to return to the main menu.\n"
                    "invalid" "if the input does not match any of these.\n\n"
                    "Only return one of the four options:" "order" "make_order" "main_menu" "invalid"
                    "Do not provide additional text or explanations."
                )
            },
            {"role": "user", "content": user_response}
        ]
    )
    return response.choices[0].message.content.strip().lower()


def interpret_disengage(user_response):
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "Your job is to interpret a user message and evaluate its meaning: "
                    "The user just selected option 3 from a menu, the option is to 'end interaction with the menu/whatsapp bot', but the user might change their mind and choose to view the menu again, or to disengage completely. Interpret their response and return one of these two answers:" 
                    "'greet' if the user wants to see menu again or 'finalize' if they want to disengage completely"
                )
            },
            {"role": "user", "content": user_response}
        ]
    )
    answer = response.choices[0].message.content.strip().lower()
    return answer