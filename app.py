from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def bot_whatsapp():
    incoming_msg = request.form.get('Body', '').strip()
    
    resp = MessagingResponse()
    msg = resp.message()

    # Opción 1: Catálogo Completo de Productos
    if incoming_msg == '1':
        msg.body(
            "📋 *CATÁLOGO DE PRODUCTOS*:\n\n"
            "🍕 *Pizzas*:\n"
            "• [P01] Pizza Muzza - $\n"
            "• [P02] Pizza Especial - $\n"
            "• [P03] Pizza Fugazzeta - $\n"
            "• [P04] Pizza - $\n"
            "• [P05] Pizza - $\n"
            "• [P06] Pizza - $\n"
            "• [P07] Pizza - $\n\n"
            "🌾 *Pizzas Sin TACC*:\n"
            "• [ST01] Pizzas Sin TACC - $\n"
            "• [ST02] Pizzas Sin TACC - $\n"
            "• [ST03] Pizzas Sin TACC - $\n\n"
            "🧊 *Congeladas*:\n"
            "• [C01] Congeladas - $10\n"
            "• [C02] Congeladas - $\n"
            "• [C03] Congeladas - $\n\n"
            "🥟 *Empanadas*:\n"
            "• [E01] Empanadas - $\n"
            "• [E02] Empanadas - $\n"
            "• [E03] Empanadas - $\n"
            "• [E04] Empanadas - $\n"
            "• [E05] Empanadas - $\n"
            "• [E06] Empanadas - $\n\n"
            "Respondé con el código del producto para agregarlo o elegí otra opción."
        )

    # Opción 2: Promociones y Combos
    elif incoming_msg == '2':
        msg.body(
            "🔥 *PROMOCIONES Y COMBOS*:\n\n"
            "⭐ [P01] Pizzas - $,,\n"
            "⭐ [P02] Pizzas - $,\n"
            "⭐ [P03] Pizzas - $,\n"
            "⭐ [P04] Pizzas - $,\n"
            "⭐ [P05] Pizzas - $,\n"
            "⭐ [P06] Pizzas - $,\n"
            "⭐ [P07] Pizzas - $,\n"
            "⭐ [ST01] Pizzas Sin TACC - $,\n"
            "⭐ [ST02] Pizzas Sin TACC - $,\n"
            "⭐ [ST03] Pizzas Sin TACC - $,\n"
            "⭐ [C01] Congeladas - $10.\n"
            "⭐ [C02] Congeladas - $\n"
            "⭐ [C03] Congeladas - $\n"
            "⭐ [E01] Empanadas - $\n"
            "⭐ [E02] Empanadas - $\n"
            "⭐ [E03] Empanadas - $\n"
            "⭐ [E04] Empanadas - $\n"
            "⭐ [E05] Empanadas - $\n"
            "⭐ [E06] Empanadas - $\n\n"
            "Respondé con el código de la promo para seleccionarla."
        )

    # Opción 3: Carrito Actual
    elif incoming_msg == '3':
        msg.body(
            "🛒 *TU CARRITO ACTUAL*:\n\n"
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
