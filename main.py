import os
import requests
from datetime import datetime
import google.generativeai as genai
from flask import Flask, request, jsonify

# Configuración de APIs
api_key = os.environ.get('GEMINI_API_KEY')
SHEETDB_URL = "TU_URL_DE_SHEETDB_AQUI" # Reemplaza con tu URL de SheetDB

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3-flash-preview')

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    
    try:
        user_query = req.get('queryResult').get('queryText')
        
        # --- Lógica de SheetDB: Guardar consulta ---
        data_to_sheet = {
            "data": [
                {
                    "Nombre": "Usuario_Telegram",
                    "Consulta": user_query,
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            ]
        }
        requests.post(SHEETDB_URL, json=data_to_sheet)
        # ------------------------------------------

        # Respuesta de Gemini
        response = model.generate_content(user_query)
        
        return jsonify({
            "fulfillmentText": response.text
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"fulfillmentText": "Error al conectar con la base de datos o la IA."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
