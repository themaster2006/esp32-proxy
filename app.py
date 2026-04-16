from flask import Flask, request, jsonify
import requests
import re
import os

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "PON_AQUI_TU_API_KEY")

def limpiar_texto(texto):
    texto = re.sub(r'\*+', '', texto)
    texto = re.sub(r'\d+\.\s+', '', texto)
    texto = re.sub(r'\n+', ' ', texto)
    if len(texto) > 200:
        texto = texto[:200] + "..."
    return texto.strip()

@app.route("/ia", methods=["POST"])
def ia():
    data_in = request.get_json(silent=True) or {}
    prompt = (data_in.get("prompt") or "").strip()

    if not prompt:
        return jsonify({"respuesta": "PROMPT_VACIO"}), 400

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"
    params = {"key": GEMINI_API_KEY}

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Eres un asistente útil. Responde en español de forma muy breve, sin markdown, sin asteriscos, sin listas. Máximo 2 oraciones. {}".format(prompt)
                    }
                ]
            }
        ]
    }

    try:
        r = requests.post(url, params=params, json=payload, timeout=30)

        try:
            res = r.json()
        except Exception:
            return jsonify({
                "respuesta": "ERROR_API",
                "detalle": "Respuesta no JSON",
                "status_code": r.status_code
            }), 500

        print("DEBUG GEMINI:", res)

        if "candidates" in res:
            parts = res["candidates"][0]["content"]["parts"]
            text_parts = [p["text"] for p in parts if "text" in p]
            respuesta = "".join(text_parts).strip()
            respuesta = limpiar_texto(respuesta)
            print("RESPUESTA LIMPIA:", respuesta)
            return jsonify({"respuesta": respuesta})

        if "error" in res:
            mensaje = res["error"].get("message", "Error desconocido")
            print("GEMINI ERROR:", mensaje)
            return jsonify({
                "respuesta": "ERROR_API",
                "detalle": mensaje
            }), 500

        return jsonify({
            "respuesta": "ERROR_NO_RESPONSE",
            "detalle": str(res)
        }), 500

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "respuesta": "ERROR_EXCEPTION",
            "detalle": str(e)
        }), 500

@app.route("/ping")
def ping():
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
