import os
from flask import Flask, request, jsonify
import google.generativeai as genai

# 1. Configuración de la IA
# Usamos os.environ para leer la clave de forma segura desde las variables de entorno de Render
api_key = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=api_key)

# Seleccionamos el modelo más eficiente para chat
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

@app.route('/')
def index():
    return "El servidor del bot está activo."

@app.route('/webhook', methods=['POST'])
def webhook():
    # 2. Recibir la petición de Dialogflow
    req = request.get_json(silent=True, force=True)
    
    try:
        # Extraer el texto que el usuario envió desde Telegram
        user_query = req.get('queryResult').get('queryText')
        
        # 3. Enviar el texto a Gemini
        # Aquí puedes añadir un "System Instruction" si quieres que sea un experto contable
        chat = model.start_chat(history=[])
        response = chat.send_message(user_query)
        
        # 4. Formatear la respuesta para Dialogflow ES
        # El campo 'fulfillmentText' es el que Dialogflow envía de vuelta a Telegram
        return jsonify({
            "fulfillmentText": response.text
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "fulfillmentText": "Lo siento, tuve un problema al procesar tu consulta con la IA."
        })

if __name__ == '__main__':
    # Render asigna un puerto automáticamente a través de la variable de entorno PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)