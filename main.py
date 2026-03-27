import os
import requests
from datetime import datetime
import google.generativeai as genai
from flask import Flask, request, jsonify

# Configuración de APIs
api_key = os.environ.get('GEMINI_API_KEY')
SHEETDB_URL = "https://sheetdb.io/api/v1/09j3wa6ux9fx7"

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3-flash-preview')

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    user_query = req.get('queryResult').get('queryText').lower()
    
    try:
        # 1. Obtener todo el inventario de SheetDB
        res = requests.get(f"{SHEETDB_URL}?sheet=Inventario")
        inventario = res.json()

        # 2. ORDENAR MODELOS POR LONGITUD (Truco para modelos Pro, Air, e)
        inventario_ordenado = sorted(inventario, key=lambda x: len(x['Modelo']), reverse=True)

        # 3. BUSCAR COINCIDENCIA EN LA PREGUNTA
        encontrado = None
        for item in inventario_ordenado:
            if item['Modelo'].lower() in user_query:
                encontrado = item
                break 

        if encontrado:
            respuesta = (f"📱 El {encontrado['Modelo']} cuesta {encontrado['Precio']}. "
                         f"Está disponible en: {encontrado['Color']}.")
            return jsonify({"fulfillmentText": respuesta})

        # 4. SI NO ESTÁ EN EL EXCEL, RESPONDER CON GEMINI
        response = model.generate_content(user_query)
        return jsonify({"fulfillmentText": response.text})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"fulfillmentText": "Hubo un problema al consultar el catálogo."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

