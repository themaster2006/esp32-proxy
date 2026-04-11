from flask import Flask, request, jsonify
import requests
import re
import os

app = Flask(__name__)

GEMINI_API_KEY = "AIzaSyAIcI_wiHFS1MPj_HiYsRdzAzWzq4KQw90"

def limpiar_texto(texto):
    texto = re.sub(r'\*+', '', texto)
    texto = re.sub(r'\d+\.\s+', '', texto)
    texto = re.sub(r'\n+', ' ', texto)
    if len(texto) > 200:
        texto = texto[:200] + "..."
    return texto.strip()

@app.route("/ia", methods=["POST"])
def ia():
    prompt = request.json.get("prompt")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"

    data = {
        "contents": [
            {
                "parts": [
                    {"text": f"Eres un asistente útil. Responde en español de forma muy breve, sin markdown, sin asteriscos, sin listas. Máximo 2 oraciones. {prompt}"}
                ]
            }
        ]
    }

    try:
        r = requests.post(url, json=data)
        res = r.json()
        print("DEBUG GEMINI:", res)

        if "candidates" in res:
            parts = res["candidates"][0]["content"]["parts"]
            text_parts = [p["text"] for p in parts if "text" in p]
            respuesta = "".join(text_parts).strip()
            respuesta = limpiar_texto(respuesta)
            print("RESPUESTA LIMPIA:", respuesta)
            return jsonify({"respuesta": respuesta})

        if "error" in res:
            print("GEMINI ERROR:", res["error"].get("message"))
            return jsonify({"respuesta": "ERROR_API"})

        return jsonify({"respuesta": "ERROR_NO_RESPONSE"})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"respuesta": "ERROR_EXCEPTION"})


@app.route("/ping")
def ping():
    return "ok"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)