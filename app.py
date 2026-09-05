import csv
import io
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# ID de la Google Sheet pública del comerciante
SPREADSHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

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

@app.route("/")
def home():
    return "¡El Bot de Pedidos de la Pizzería está activo y funcionando correctamente! 🍕🤖"

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

    if "hola" in incoming_msg or "menu" in incoming_msg or "inicio" in incoming_msg:
        usuario["estado"] = "MENU"
        usuario["carrito"] = []
        msg.body(
            "¡Hola! 👋 Bienvenido a nuestro servicio de pedidos automáticos.\n\n"
            "¿Qué te gustaría hacer hoy?\n"
            "1️⃣ Ver Catálogo de Productos\n"
            "2️⃣ Ver Promociones y Combos\n"
            "3️⃣ Ver mi Carrito actual\n\n"
            "Respondé con el número de la opción."
        )

    elif estado_actual == "MENU":
        if incoming_msg == "1":
            registros = leer_google_sheet_publica("Menú y Productos")
            if registros:
                texto = "📋 *CATÁLOGO DE PRODUCTOS*:\n\n"
                for r in registros[:10]:
                    texto += f"🔹 *[{r.get('Código')}]* {r.get('Producto / Variedad')} - ${r.get('Precio ($)')}\n"
                texto += "\nRespondé con el *Código* del producto (ej: P01) para sumarlo, o *0* para volver."
                usuario["estado"] = "ESPERANDO_PRODUCTO"
                msg.body(texto)
            else:
                msg.body("⚠️ Error al leer el catálogo en tiempo real.")

        elif incoming_msg == "2":
            registros = leer_google_sheet_publica("Promociones y Combos")
            if registros:
                texto = "🔥 *PROMOCIONES Y COMBOS*:\n\n"
                for r in registros:
                    texto += f"⭐ *[{r.get('Código Combo')}]* {r.get('Nombre de la Promoción')} - *${r.get('Precio Promo ($)')}*\n"
                texto += "\nRespondé con el *Código* de la promo (ej: PR01), o *0* para volver."
                usuario["estado"] = "ESPERANDO_PRODUCTO"
                msg.body(texto)
            else:
                msg.body("⚠️ Error al leer las promos.")

        elif incoming_msg == "3":
            if not usuario["carrito"]:
                msg.body("🛒 Tu carrito está vacío. Escribí *menu* para ver las opciones.")
            else:
                detalle = "🛒 *Tu Carrito Actual*:\n"
                total = 0
                for item in usuario["carrito"]:
                    detalle += f"- {item['nombre']}: ${item['precio']}\n"
                    total += float(item['precio'])
                detalle += f"\nTotal a pagar: *${total}*\n\nRespondé *CONFIRMAR* para finalizar o *MENU* para seguir comprando."
                usuario["estado"] = "CONFIRMACION"
                msg.body(detalle)
        else:
            msg.body("Opción no válida. Por favor respondé 1, 2 o 3.")

    elif estado_actual == "ESPERANDO_PRODUCTO":
        if incoming_msg == "0":
            usuario["estado"] = "MENU"
            msg.body("Volviste al menú principal. Escribí 1, 2 o 3.")
        else:
            encontrado = None
            for solapa in ["Menú y Productos", "Promociones y Combos"]:
                registros = leer_google_sheet_publica(solapa)
                for r in registros:
                    cod = str(r.get('Código') or r.get('Código Combo') or '').strip().lower()
                    if cod == incoming_msg:
                        nombre = r.get('Producto / Variedad') or r.get('Nombre de la Promoción')
                        precio = r.get('Precio ($)') or r.get('Precio Promo ($)')
                        encontrado = {"nombre": nombre, "precio": precio}
                        break
                if encontrado:
                    break

            if encontrado:
                usuario["carrito"].append(encontrado)
                msg.body(f"✅ ¡Agregado: *{encontrado['nombre']}* (${encontrado['precio']})!\n\n¿Querés otro producto (escribí su código) o ver tu carrito escribiendo *3*?")
            else:
                msg.body("❌ Código no encontrado. Verificá el código en el catálogo o escribí *0* para volver.")

    elif estado_actual == "CONFIRMACION":
        if "confirmar" in incoming_msg:
            msg.body("🎉 ¡Pedido confirmado con éxito! El local ya lo está preparando. ¡Muchas gracias! 🙌")
            usuario["carrito"] = []
            usuario["estado"] = "MENU"
        else:
            usuario["estado"] = "MENU"
            msg.body("Operación cancelada. Escribí *hola* para empezar de nuevo.")

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True) 
