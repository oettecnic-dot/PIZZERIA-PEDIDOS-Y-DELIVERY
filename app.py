import os
import pandas as pd
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# --- CONFIGURACIÓN DE LA PLANILLA DE GOOGLE SHEETS ---
# Pegá acá el ID de la Google Sheet del comerciante (lo sacás de la URL de su planilla)
# Ejemplo de URL: https://docs.google.com/spreadsheets/d/1BxiMVs0XRA.../edit
SPREADSHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms" # Reemplazá con tu ID real

def leer_google_sheet_publica(nombre_pestana):
    try:
        # URL oficial de Google Sheets para exportar solapas específicas a formato CSV al instante
        # (Nota: Asegurate de que la planilla esté compartida como "Cualquier persona con el enlace puede ver")
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={nombre_pestana}"

        # Leemos los datos con Pandas
        df = pd.read_csv(url)
        # Convertimos el DataFrame a lista de diccionarios para que el bot lo procese fácil
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Error al leer la planilla pública: {e}")
        return []

# Diccionario temporal en memoria para los carritos de cada cliente
sesiones_usuarios = {}

@app.route("/webhook", methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip().lower()
    sender_number = request.values.get('From', '')

    resp = MessagingResponse()
    msg = resp.message()

    if sender_number not in sesion_usuario := sesiones_usuarios.setdefault(sender_number, {"estado": "INICIO", "carrito": []}):
        pass
    usuario = sesiones_usuarios[sender_number]
    estado_actual = usuario["estado"]

    # --- FLUJO DEL BOT ---
    if "hola" in incoming_msg or "menu" in incoming_msg:
        usuario["estado"] = "MENU"
        usuario["carrito"] = []
        msg.body(
            "¡Hola! 👋 Bienvenido a nuestro servicio de pedidos automáticos.\n\n"
            "¿Qué te gustaría hacer?\n"
            "1️⃣ Ver Catálogo de Productos\n"
            "2️⃣ Ver Promociones y Combos\n"
            "3️⃣ Ver mi Carrito\n\n"
            "Respondé con el número de la opción."
        )

    elif estado_actual == "MENU":
        if incoming_msg == "1":
            # Lee en tiempo real la solapa "Menú y Productos" directamente de la nube del cliente
            registros = leer_google_sheet_publica("Menú y Productos")
            if registros:
                texto = "📋 *CATÁLOGO EN VIVO*:\n\n"
                for r in registros[:10]: # Mostramos los primeros 10
                    texto += f"🔹 *[{r.get('Código')}]* {r.get('Producto / Variedad')} - ${r.get('Precio ($)')}\n"
                texto += "\nRespondé con el *Código* del producto para sumarlo, o *0* para volver."
                usuario["estado"] = "ESPERANDO_PRODUCTO"
                msg.body(texto)
            else:
                msg.body("⚠️ No se pudo leer el catálogo en este momento. Verificá que la planilla sea pública.")

        elif incoming_msg == "2":
            # Lee en tiempo real la solapa "Promociones y Combos"
            registros = leer_google_sheet_publica("Promociones y Combos")
            if registros:
                texto = "🔥 *PROMOCIONES EN VIVO*:\n\n"
                for r in registros:
                    texto += f"⭐ *[{r.get('Código Combo')}]* {r.get('Nombre de la Promoción')} - *${r.get('Precio Promo ($)')}*\n"
                texto += "\nRespondé con el *Código* de la promo, o *0* para volver."
                usuario["estado"] = "ESPERANDO_PRODUCTO"
                msg.body(texto)
            else:
                msg.body("⚠️ No se pudieron leer las promos.")

        elif incoming_msg == "3":
            if not usuario["carrito"]:
                msg.body("🛒 Tu carrito está vacío.")
            else:
                detalle = "🛒 *Tu Carrito*:\n"
                total = 0
                for item in usuario["carrito"]:
                    detalle += f"- {item['nombre']}: ${item['precio']}\n"
                    total += item['precio']
                detalle += f"\nTotal: *${total}*\n\nRespondé *CONFIRMAR* para enviar tu pedido."
                usuario["estado"] = "CONFIRMACION"
                msg.body(detalle)
        else:
            msg.body("Por favor respondé 1, 2 o 3.")

    elif estado_actual == "ESPERANDO_PRODUCTO":
        if incoming_msg == "0":
            usuario["estado"] = "MENU"
            msg.body("Volviste al menú principal. Escribí 1, 2 o 3.")
        else:
            # Buscamos en ambas solapas en tiempo real
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
                msg.body("❌ Código no encontrado. Verificá en el catálogo o escribí *0* para volver.")

    elif estado_actual == "CONFIRMACION":
        if "confirmar" in incoming_msg:
            msg.body("🎉 ¡Pedido confirmado! El comercio ya fue notificado y lo está preparando.")
            usuario["carrito"] = []
            usuario["estado"] = "MENU"
        else:
            usuario["estado"] = "MENU"
            msg.body("Operación cancelada. Escribí *hola* para empezar de nuevo.")

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
