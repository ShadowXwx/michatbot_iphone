import os
import google.generativeai as genai
from flask import Flask, request, jsonify

# 1. Configuración de la API Key (se lee desde las variables de entorno de Render)
api_key = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=api_key)

# 2. Definición del modelo (usamos la versión preview que aparece en tu consola)
model = genai.GenerativeModel('gemini-3-flash-preview')

app = Flask(__name__)

@app.route('/')
def index():
    return "Servidor del Bot Activo y Conectado"

@app.route('/webhook', methods=['POST'])
def webhook():
    # Recibir la petición de Dialogflow
    req = request.get_json(silent=True, force=True)
    
    try:
        # Extraer el texto del usuario
        user_query = req.get('queryResult').get('queryText')
        
        # Generar la respuesta con la IA
        # Añadimos un pequeño manejo de historial vacío para estabilidad
        chat = model.start_chat(history=[])
        response = chat.send_message(user_query)
        
        # Enviar de vuelta a Dialogflow/Telegram
        return jsonify({
            "fulfillmentText": response.text
        })
        
    except Exception as e:
        print(f"Error detectado: {str(e)}")
        return jsonify({
            "fulfillmentText": "Lo siento, hubo un error interno en la conexión con la IA."
        })

if __name__ == '__main__':
    # Render asigna el puerto automáticamente
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
