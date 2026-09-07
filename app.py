from flask import Flask, request, render_template_string
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

HTML_CHAT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Pizzería - Chat</title>
</head>
<body>
    <h1>Sistema de Pedidos y Delivery</h1>
    <p>El bot de WhatsApp está activo.</p>
</body>
</html>
"""

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1uzGGa7y_hiZ5B1PKD_YiY0491V2b5QoRoF0VDyYvh0"

# 1. Ruta principal para ver la interfaz en el navegador (GET)
@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_CHAT)

# 2. Ruta del Webhook que procesa los mensajes (para la web y para Twilio)
@app.route("/webhook", methods=["POST"])
def webhook():
    user_message = ""

    # Revisar si viene de nuestra interfaz web (JSON)
    data = request.get_json(silent=True)
    if data and "message" in data:
        user_message = data.get("message", "")
    else:
        # Si no es JSON, revisamos si viene de Twilio (WhatsApp Sandbox)
        user_message = request.values.get("Body", "")

    user_message = str(user_message).lower().strip()

    # Creamos la respuesta oficial para Twilio usando TwiML
    resp = MessagingResponse()
    msg = resp.message()

    # Lógica de respuestas del bot (incluyendo variantes con y sin tilde)
    if "catalogo" in user_message or "catálogo" in user_message:
        msg.body("Aquí tienes nuestro catálogo de pizzas y promos disponibles. ¡Escribe tu pedido cuando estés listo!")
    elif "hola" in user_message:
        msg.body("¡Hola! Bienvenido al sistema de pedidos. Escribe 'catalogo' para ver nuestras opciones.")
    else:
        msg.body("No he entendido bien tu mensaje. Escribe 'hola' para empezar o 'catalogo' para ver los productos.")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True) 
