# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from sklearn.ensemble import IsolationForest
import pandas as pd
from twilio.rest import Client
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)
model = None
# Muat variabel dari .env
load_dotenv()

uri = "mongodb+srv://timtujuh:vV2WEXiqjSTmPevl@clustertimtujuh.8p34h.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTimTujuh"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["TimTujuhDatabase"]
collection = db["MySensorData"]

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
WHATSAPP_TO = os.getenv("WHATSAPP_TO")

client_twilio = Client(TWILIO_SID, TWILIO_TOKEN)

def send_whatsapp_message(body):
    try:
        message = client_twilio.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            body=body,
            to=WHATSAPP_TO
        )
        print("[WA] Notifikasi terkirim:", message.sid)
    except Exception as e:
        print("[WA] Gagal kirim:", e)

@app.route("/sensor", methods=["POST"])
def receive_data():
    try:
        data = request.json
        required_keys = {"humidity", "temperature", "motion", "ldr"}
        if not all(key in data and isinstance(data[key], (int, float, bool)) for key in required_keys):
            return jsonify({"error": "Format data tidak valid!"}), 400

        data["timestamp"] = datetime.utcnow()

        if model:
            df_input = pd.DataFrame([{
                "temperature": data["temperature"],
                "humidity": data["humidity"],
                "ldr": data["ldr"]
            }])
            prediction = model.predict(df_input)[0]
            data["anomaly"] = int(prediction)
            if prediction == -1:
                send_whatsapp_message(
                    f"🚨 Deteksi Anomali!\n"
                    f"Suhu: {data['temperature']} °C\n"
                    f"Kelembapan: {data['humidity']} %\n"
                    f"LDR: {data['ldr']}\n"
                    f"Gerakan: {'Ya' if data['motion'] else 'Tidak'}\n"
                    f"Timestamp: {data['timestamp']}"
                )
        else:
            data["anomaly"] = 1

        collection.insert_one(data)

        # ✅ Retrain model setiap 100 data
        doc_count = collection.count_documents({})
        if doc_count > 0 and doc_count % 15 == 0:
            train_model()
            print("[INFO] Model dilatih ulang otomatis.")

        return jsonify({
            "message": "Data berhasil disimpan",
            "anomaly": data["anomaly"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/sensor", methods=["GET"])
def get_data():
    data = list(collection.find({}, {"_id": 0}).sort("timestamp", -1))
    return jsonify(data), 200


def train_model():
    global model
    # Ambil data awal dari MongoDB
    data = list(collection.find({}, {"_id": 0}))
    df = pd.DataFrame(data)
    df = df[["temperature", "humidity", "ldr"]].dropna()
    
    if not df.empty:
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(df)
        
@app.route("/model_status", methods=["GET"])
def model_status():
    status = "trained" if model else "not trained"
    return jsonify({"model_status": status})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)