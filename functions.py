
def get_product_list():
    """Returns the raw product list as a dictionary."""
    return {
        "Origen Animal": {
            "Suprema Pollo (1kg)": 400,
            "Huevos Docena": 200,
            "Milanesas (1kg)": 560,
        },
        "Granos y Cereales": {
            "Granola (500g)": 320,
            "Quinoa (500g)": 400,
            "Arroz (1kg)": 160,
            "Arroz integral (1kg)": 240,
            "Avena (1kg)": 192,
        },
        "Frutas y Verduras": {
            "Bananas (1kg)": 128,
            "Paltas (Unidad)": 80,
            "Papas (1kg)": 64,
            "Boniatos (1kg)": 80,
        },
        "Frutos Secos y Semillas": {
            "Nueces (200g)": 240,
            "Almendras (200g)": 288,
            "Castañas de Cajú (200g)": 320,
        },
        "Legumbres": {
            "Porotos negros (500g)": 128,
            "Porotos manteca (500g)": 144,
            "Garbanzo (500g)": 160,
            "Lentejas (500g)": 112,
        },
        "Aceites": {
            "Aceite de Oliva (500ml)": 480,
        },
        "Otros": {
            "Alimento Mascota (3kg)": 960,
        }
    }


def format_product_list(raw_product_list=get_product_list()):
    """Formats the raw product list into a user-friendly string."""
    formatted_list = "Lista de Productos Disponibles:\n\n"
    for category, items in raw_product_list.items():
        formatted_list += f"🔸 {category}:\n"
        for product, price in items.items():
            formatted_list += f"  • {product}: ${price}\n"
        formatted_list += "\n"
    return formatted_list.strip()
