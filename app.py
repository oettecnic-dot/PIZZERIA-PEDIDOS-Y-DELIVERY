from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def bot_whatsapp():
    # Obtenemos el mensaje que envía el usuario y limpiamos espacios vacíos
    incoming_msg = request.form.get('Body', '').strip()
    
    resp = MessagingResponse()
    msg = resp.message()

    # Opción 1: Catálogo de Productos
    if incoming_msg == '1':
        msg.body(
            "📋 *CATÁLOGO DE PRODUCTOS*:\n\n"
            "🍕 [P01] Pizza Muzza - $...\n"
            "🍕 [P02] Pizza Especial - $...\n"
            "🍕 [P03] Pizza Fugazzeta - $...\n"
            "🥟 [E01] Empanada de Carne - $...\n"
            "🥟 [E02] Empanada de Jamón y Queso - $...\n\n"
            "Respondé con el código del producto para agregarlo o elegí otra opción."
        )

    # Opción 2: Promociones y Combos (CORREGIDA)
    elif incoming_msg == '2':
        msg.body(
            "🔥 *PROMOCIONES Y COMBOS*:\n\n"
            "⭐ [C01] Promo 1: 2 Pizzas Muzza + Fainá - $...\n"
            "⭐ [C02] Promo 2: 1 Pizza Especial + 6 Empanadas - $...\n"
            "⭐ [C03] Promo 3 (Congeladas): Pack x3 Pizzas - $10...\n\n"
            "Respondé con el código de la promo para seleccionarla."
        )

    # Opción 3: Carrito Actual
    elif incoming_msg == '3':
        msg.body(
            "🛒 *TU CARRITO ACTUAL*:\n\n"
            "Aún no tenés productos cargados en tu pedido.\n\n"
            "Escribí el código de lo que quieras sumar."
        )

    # Mensaje por defecto si escribe cualquier otra cosa
    else:
        msg.body(
            "¡Hola! 👋 Bienvenido a nuestro servicio de pedidos automáticos.\n\n"
            "¿Qué te gustaría hacer hoy?\n"
            "1️⃣ Ver Catálogo de Productos\n"
            "2️⃣ Ver Promociones y Combos\n"
            "3️⃣ Ver mi Carrito actual\n\n"
            "Respondé con el número de la opción."
        )

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000) 
