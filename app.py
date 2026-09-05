import csv
import io
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

SPREADSHEET_ID = "1uzGGa7y_hIZ5BWlPKD_YIyO491V2b5QOroFODVDyvh0"

def leer_google_sheet_publica(nombre_pestana):
    try:
        # Método 1: Exportación directa por nombre de solapa
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={nombre_pestana}"
        response = requests.get(url)
        if response.status_code == 200 and len(response.content) > 0:
            decoded_content = response.content.decode('utf-8')
            reader = csv.reader(io.StringIO(decoded_content))
            filas = list(reader)
            if len(filas) > 1:
                return filas[1:]
        
        # Método 2: Exportación alternativa como archivo CSV web
        url_alt = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&sheet={nombre_pestana}"
        response_alt = requests.get(url_alt)
        if response_alt.status_code == 200:
            decoded_content = response_alt.content.decode('utf-8')
            reader = csv.reader(io.StringIO(decoded_content))
            filas = list(reader)
            return filas[1:] if len(filas) > 1 else []
            
    except Exception as e:
        print(f"Error al leer la planilla web: {e}")
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
    elif incoming_msg == "3":
        usuario["estado"] = "CONFIRMACION"
        if not usuario["carrito"]:
            msg.body("🛒 Tu carrito está vacío. Escribí *1* para ver el catálogo o *hola* para empezar.")
        else:
            detalle = "🛒 *Tu Carrito Actual*:\n"
            total = 0
            for item in usuario["carrito"]:
                precio_crudo = item['precio']
                precio_limpio = ''.join(c for c in precio_crudo if c.isdigit() or c in '.,')
                precio_num_str = precio_limpio.replace('.', '').replace(',', '.')
                
                try:
                    valor = float(precio_num_str)
                except ValueError:
                    valor = 0.0
                
                total += valor
                detalle += f"- {item['nombre']}: ${precio_limpio}\n"
                
            detalle += f"\nTotal a pagar: *${total:,.2f}*\n\nRespondé *CONFIRMAR* para finalizar o *MENU* para seguir comprando."
            msg.body(detalle)

    elif estado_actual == "MENU":
        if incoming_msg == "1":
            filas = leer_google_sheet_publica("Menu")
            if filas:
                texto = "📋 *CATÁLOGO DE PRODUCTOS*:\n\n"
                for r in filas:
                    if len(r) >= 5:
                        codigo = r[0].strip()
                        producto = r[2].strip()
                        precio_crudo = r[4].strip()
                        precio_limpio = ''.join(c for c in precio_crudo if c.isdigit() or c in '.,')
                        if codigo:
                            texto += f"🔹 *[{codigo}]* {producto} - ${precio_limpio}\n"
                texto += "\nRespondé con el *Código* del producto para sumarlo, o *3* para ver tu carrito."
                usuario["estado"] = "ESPERANDO_PRODUCTO"
                msg.body(texto)
            else:
                msg.body("⚠️ No se pudieron leer los productos. Verificá que la solapa de Google Sheets se llame exactamente 'Menu'.")

        elif incoming_msg == "2":
            filas = leer_google_sheet_publica("Promos")
            if filas:
                texto = "🔥 *PROMOCIONES Y COMBOS*:\n\n"
                for r in filas:
                    if len(r) >= 4:
                        codigo = r[0].strip()
                        promo = r[1].strip()
                        precio_crudo = r[3].strip()
                        precio_limpio = ''.join(c for c in precio_crudo if c.isdigit() or c in '.,')
                        if codigo:
                            texto += f"⭐ *[{codigo}]* {promo} - *${precio_limpio}*\n"
                texto += "\nRespondé con el *Código* de la promo, o *3* para ver tu carrito."
                usuario["estado"] = "ESPERANDO_PRODUCTO"
                msg.body(texto)
            else:
                msg.body("⚠️ No se pudieron leer las promociones. Verificá que la solapa se llame 'Promos'.")
        else:
            msg.body("Opción no válida. Por favor respondé 1, 2 o 3.")

    elif estado_actual == "ESPERANDO_PRODUCTO":
        if incoming_msg == "0":
            usuario["estado"] = "MENU"
            msg.body("Volviste al menú principal. Escribí 1, 2 o 3.")
        else:
            encontrado = None
            for r in leer_google_sheet_publica("Menu"):
                if len(r) >= 5 and r[0].strip().lower() == incoming_msg:
                    encontrado = {"nombre": r[2].strip(), "precio": r[4].strip()}
                    break
            
            if not encontrado:
                for r in leer_google_sheet_publica("Promos"):
                    if len(r) >= 4 and r[0].strip().lower() == incoming_msg:
                        encontrado = {"nombre": r[1].strip(), "precio": r[3].strip()}
                        break

            if encontrado:
                usuario["carrito"].append(encontrado)
                precio_crudo = encontrado['precio']
                precio_limpio = ''.join(c for c in precio_crudo if c.isdigit() or c in '.,')
                msg.body(f"✅ ¡Agregado: *{encontrado['nombre']}* (${precio_limpio})!\n\n¿Querés otro producto (escribí su código) o escribí *3* para ver tu carrito y finalizar?")
            else:
                msg.body("❌ Código no encontrado. Verificá el código en el catálogo, escribí *0* para volver o *3* para ver tu carrito.")

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
