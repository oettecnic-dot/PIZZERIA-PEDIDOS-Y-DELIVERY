from flask import Flask, request, jsonify, render_template_string
from twilio.twiml.messaging_response import MessagingResponse
import requests
import csv
from io import StringIO

app = Flask(__name__)

# Interfaz visual simple para probar el bot
HTML_CHAT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Asistente de Stock - Google Sheets</title>
    <style>
        body { font-family: Arial, sans-serif; background: #e5ddd5; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .chat-container { width: 100%; max-width: 500px; background: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); overflow: hidden; display: flex; flex-direction: column; height: 80vh; }
        .chat-header { background: #075e54; color: white; padding: 15px; text-align: center; font-size: 18px; font-weight: bold; }
        .chat-box { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .message { padding: 10px 15px; border-radius: 7px; max-width: 75%; line-height: 1.4; white-space: pre-wrap; }
        .user { background: #dcf8c6; align-self: flex-end; }
        .bot { background: #f1f0f0; align-self: flex-start; }
        .chat-input { display: flex; padding: 10px; background: #f0f0f0; border-top: 1px solid #ddd; }
        .chat-input input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; outline: none; }
        .chat-input button { background: #075e54; color: white; border: none; padding: 10px 15px; margin-left: 5px; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">Asistente de Stock</div>
        <div class="chat-box" id="chatBox">
            <div class="message bot">¡Hola! 😊 ¿Qué producto deseas consultar hoy o prefieres ver el catálogo completo?</div>
        </div>
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="Escribe un mensaje..." onkeypress="if(event.key === 'Enter') sendMessage()">
            <button onclick="sendMessage()">Enviar</button>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const chatBox = document.getElementById('chatBox');
            const text = input.value.trim();
            if(!text) return;

            chatBox.innerHTML += `<div class="message user">${text}</div>`;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/webhook', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();

                chatBox.innerHTML += `<div class="message bot">${data.message}</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            } catch (error) {
                chatBox.innerHTML += `<div class="message bot">Error de conexión con el servidor.</div>`;
            }
        }
    </script>
</body>
</html>
"""

# URL de exportación CSV directa con el ID y el gid exacto de tu planilla
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1R8p60ENEFrB5yQcvPcog7fv5Ama3vyFKUR9hp/export?format=csv&gid=1835820971"

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
    respuesta = "¡Hola! Bienvenido al sistema."

    try:
        # Detección de saludos
        if not user_message or user_message in ["hola", "buen dia", "buenas", "que tal", "saludos", "ola", "hi"] or "hola" in user_message:
            respuesta = "¡Hola! 😊 ¿Qué producto deseas consultar hoy o prefieres ver el catálogo completo?"

        else:
            # Descargar los datos dinámicamente desde Google Sheets
            response = requests.get(SHEET_CSV_URL)
            response.raise_for_status()
            
            # Procesar el texto plano como un archivo CSV línea por línea de forma ilimitada
            f = StringIO(response.text)
            lector = csv.reader(f)
            
            filas = list(lector)
            if len(filas) <= 1:
                return jsonify({"message": "La planilla está vacía."})

            # Cabecera (fila 0) y datos (desde la fila 1 en adelante, sin límite)
            lineas_datos = filas[1:]

            # Si pide catálogo completo
            if any(k in user_message for k in ["catalo", "catál", "lista", "todo", "stock"]):
                lista_productos = []
                for partes in lineas_datos:
                    if len(partes) >= 3 and partes[0].strip():
                        producto = partes[0].strip()
                        cantidad = partes[1].strip()
                        precio = "".join(partes[2:]).replace('$', '').strip()
                        lista_productos.append(f"• {producto} - Stock: {cantidad} - Precio: ${precio}")

                respuesta = "📋 Catálogo disponible:\n" + "\n".join(lista_productos) if lista_productos else "El catálogo está vacío."

            else:
                # Búsqueda flexible (permite buscar escribiendo las primeras letras o parte del nombre)
                encontrado = False
                for partes in lineas_datos:
                    if len(partes) >= 3 and partes[0].strip():
                        producto = partes[0].strip()
                        producto_lower = producto.lower()
                        
                        # Comprueba si lo que escribió el usuario está contenido en el nombre del producto
                        if user_message in producto_lower:
                            cantidad = partes[1].strip()
                            precio = "".join(partes[2:]).replace('$', '').strip()
                            respuesta = f"🔹 {producto}\n📊 Stock disponible: {cantidad}\n💰 Precio: ${precio}"
                            encontrado = True
                            break

                if not encontrado:
                    respuesta = f"No encontré el producto '{user_message}'. Escribe 'catálogo' para ver la lista completa."

    except Exception as e:
        respuesta = f"Ocurrió un error al conectar con Google Sheets: {str(e)}"

    # Si la petición viene de Twilio, respondemos con formato TwiXML (WhatsApp)
    if "Body" in request.values:
        twiliow_resp = MessagingResponse()
        twiliow_resp.message(respuesta)
        return str(twiliow_resp)

    # Si viene de nuestra interfaz web, respondemos en JSON
    return jsonify({"message": respuesta})

if __name__ == "__main__":
    app.run(debug=True) 
