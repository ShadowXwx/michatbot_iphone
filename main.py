import os
import requests
from datetime import datetime
import google.generativeai as genai
from flask import Flask, request, jsonify

# Configuración de APIs
api_key = os.environ.get('GEMINI_API_KEY')
SHEETDB_URL = "https://sheetdb.io/api/v1/09j3wa6ux9fx7" # Reemplaza con tu URL de SheetDB

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3-flash-preview')

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    user_query = req.get('queryResult').get('queryText').lower()
    
    try:
        # LÓGICA 1: GUARDAR PRECIO Y COLOR (Ej: "Guardar iPhone 15, 20000, Azul")
        if "guardar" in user_query and "," in user_query:
            partes = [p.strip() for p in user_query.replace("guardar", "").split(",")]
            if len(partes) >= 3:
                data = {"data": [{"Modelo": partes[0], "Precio": partes[1], "Color": partes[2]}]}
                requests.post(f"{SHEETDB_URL}?sheet=Inventario", json=data)
                return jsonify({"fulfillmentText": f"✅ Registrado: {partes[0]} {partes[2]} a ${partes[1]}."})

        # LÓGICA 2: REGISTRAR VENTA (Ej: "Venta a Vicente de 2 iPhone 15")
        if "venta" in user_query:
            # Usamos a Gemini para extraer los datos de la frase de venta de forma inteligente
            prompt_venta = f"Extrae Cliente, Modelo y Cantidad de esta frase: '{user_query}'. Responde solo en formato CSV: cliente,modelo,cantidad"
            res_ia = model.generate_content(prompt_venta).text.strip().split(",")
            
            data_venta = {"data": [{
                "Cliente": res_ia[0], 
                "Modelo": res_ia[1], 
                "Cantidad": res_ia[2], 
                "Fecha": datetime.now().strftime("%d/%m/%Y")
            }]}
            requests.post(f"{SHEETDB_URL}?sheet=Ventas", json=data_venta)
            return jsonify({"fulfillmentText": f"💰 Venta anotada: {res_ia[2]} unidad(es) de {res_ia[1]} para {res_ia[0]}."})

        # LÓGICA 3: CONSULTAR PRECIO (Cualquier otra pregunta va a Gemini)
        # Primero buscamos en el Excel si existe el modelo
        inventario = requests.get(f"{SHEETDB_URL}?sheet=Inventario").json()
        for item in inventario:
            if item['Modelo'].lower() in user_query:
                return jsonify({"fulfillmentText": f"📱 El {item['Modelo']} ({item['Color']}) cuesta ${item['Precio']}."})

        # Si no está en el Excel, responde Gemini normal
        response = model.generate_content(user_query)
        return jsonify({"fulfillmentText": response.text})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"fulfillmentText": "Hubo un error al procesar la solicitud."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
