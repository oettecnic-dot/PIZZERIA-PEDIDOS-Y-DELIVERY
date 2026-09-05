import csv
import io
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

SPREADSHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms" # Reemplazá con tu ID real de la planilla

def leer_google_sheet_publica(nombre_pestana):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={nombre_pestana}"
        response = requests.get(url)
        if response.status_code == 200:
            decoded_content = response.content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded_content))
            return list(reader)
    except Exception as e:
        print(f"Error al leer la planilla: {e}")
    return []

sesiones_usuarios = {}

@app.route("/webhook", methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip().lower()
    sender_number = request.values.get('From', '')
    
    resp = MessagingResponse()
    msg = resp.message()

    if sender_number not in sesiones_usuarios:
        sesiones_usuarios[sender_number] = {"estado": "INICIO", "carrito": []}
    
    usuario = sesiones_usuarios[sender_number]
    estado_actual = usuario["estado"]

    if "hola" in incoming_msg or "menu" in incoming_msg:
        usuario["estado"] = "MENU"
        usuario["carrito"] = []
        msg.body("¡Hola! 👋 Bienvenido a nuestro servicio de pedidos.\n\n1️⃣ Ver Catálogo\n2️⃣ Ver Promos\n3️⃣ Ver Carrito\n\nRespondé 1, 2 o 3.")
    elif estado_actual == "MENU":
        if incoming_msg == "1":
            registros = leer_google_sheet_publica("Menú y Productos")
            if registros:
                texto = "📋 *CATÁLOGO*:\n\n"
                for r in registros[:10]:
                    texto += f"🔹 *[{r.get('Código')}]* {r.get('Producto / Variedad')} - ${r.get('Precio ($)')}\n"
                msg.body(texto)
            else:
                msg.body("⚠️ Error al leer el catálogo.")
        else:
            msg.body("Respondé 1 para ver el menú.")
    
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True) 
