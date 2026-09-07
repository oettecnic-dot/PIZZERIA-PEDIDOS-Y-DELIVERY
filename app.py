from flask import Flask, request, render_template_string
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd

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

# URL corregida para exportar la planilla de Google Sheets a CSV
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1uzGGa7y_hiZ5B1PKD_YiY0491V2b5QoRoF0VDyYvh0/export?format=csv"

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

    # Lógica de respuestas del bot leída desde Google Sheets
    if "catalogo" in user_message or "catálogo" in user_message:
        try:
            # Descarga y lee los datos de la planilla en formato CSV
            df = pd.read_csv(SHEET_CSV_URL)
            
            catalogo_texto = "🍕 *Catálogo y Promos* 🍕\n\n"
            for index, row in df.iterrows():
                # Toma las primeras columnas de la fila (ej. nombre del producto y precio)
                nombre = str(row.iloc[0]) if len(row) > 0 else ""
                precio = str(row.iloc[1]) if len(row) > 1 else ""
                catalogo_texto += f"• {nombre}: ${precio}\n"
                
            msg.body(catalogo_texto)
        except Exception as e:
            msg.body("No pudimos cargar el catálogo en este momento. Por favor, intenta más tarde.")
    elif "hola" in user_message:
        msg.body("¡Hola! Bienvenido al sistema de pedidos. Escribe 'catalogo' para ver nuestras opciones.")
    else:
        msg.body("No he entendido bien tu mensaje. Escribe 'hola' para empezar o 'catalogo' para ver los productos.")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True) 
