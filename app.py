from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def bot_whatsapp():
    incoming_msg = request.form.get('Body', '').strip()
    
    resp = MessagingResponse()
    msg = resp.message()

    # Opción 1: Catálogo Completo Extenso
    if incoming_msg == '1':
        msg.body(
            "📋 CATÁLOGO DE PRODUCTOS:\n\n"
            "🍕 Pizzas:\n"
            "• [P01] Pizza Muzza - $8500\n"
            "• [P02] Pizza Especial - $9500\n"
            "• [P03] Pizza Fugazzeta - $9000\n"
            "• [P04] Pizza Napolitana - $9800\n"
            "• [P05] Pizza Calabresa - $9800\n"
            "• [P06] Pizza Jamón y Morrones - $10200\n"
            "• [P07] Pizza Cuatro Quesos - $10500\n\n"
            "🌾 Pizzas Sin TACC:\n"
            "• [ST01] Pizzas Sin TACC Muzza - $9500\n"
            "• [ST02] Pizzas Sin TACC Especial - $10500\n"
            "• [ST03] Pizzas Sin TACC Fugazzeta - $10000\n\n"
            "🧊 Congeladas:\n"
            "• [C01] Congeladas Muzza - $10000\n"
            "• [C02] Congeladas Especial - $11000\n"
            "• [C03] Congeladas Fugazzeta - $10500\n\n"
            "🥟 Empanadas:\n"
            "• [E01] Empanada de Carne - $1200\n"
            "• [E02] Empanada de Jamón y Queso - $1200\n"
            "• [E03] Empanada de Pollo - $1200\n"
            "• [E04] Empanada de Verdura - $1200\n"
            "• [E05] Empanada de Cebolla y Queso - $1200\n"
            "• [E06] Empanada de Roquefort - $1300\n\n"
            "Respondé con el código del producto para agregarlo o elegí otra opción."
        )

    # Opción 2: Promociones y Combos
    elif incoming_msg == '2':
        msg.body(
            "🔥 PROMOCIONES Y COMBOS:\n\n"
            "⭐ [PROMO1] 2 Pizzas Muzza + Fainá - $15000\n"
            "⭐ [PROMO2] 1 Pizza Especial + 6 Empanadas - $16000\n"
            "⭐ [PROMO3] Pack x3 Pizzas a elección - $24000\n\n"
            "Respondé con el código de la promo para seleccionarla."
        )

    # Opción 3: Carrito Actual
    elif incoming_msg == '3':
        msg.body(
            "🛒 TU CARRITO ACTUAL:\n\n"
            "Aún no tenés productos cargados en tu pedido.\n\n"
            "Escribí el código de lo que quieras sumar."
        )

    # Menú Principal por defecto
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
