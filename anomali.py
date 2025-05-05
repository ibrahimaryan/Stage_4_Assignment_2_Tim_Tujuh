from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np
from datetime import timedelta

# 1. Koneksi ke MongoDB Atlas
uri = "mongodb+srv://timtujuh:vV2WEXiqjSTmPevl@clustertimtujuh.8p34h.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTimTujuh"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["TimTujuhDatabase"]
collection = db["MySensorData"]

# 2. Ambil data sensor dari koleksi
data = list(collection.find({}, {"_id": 0}))
df = pd.DataFrame(data)

# 3. Preprocessing
if 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'])

df_clean = df[["temperature", "humidity", "ldr"]].dropna()

# 4. Model deteksi anomali (Isolation Forest)
model = IsolationForest(contamination=0.1, random_state=42)
df_clean["anomaly"] = model.fit_predict(df_clean)  # -1 = anomali, 1 = normal

# 5. Gabungkan kembali ke dataframe utama
df["anomaly"] = df_clean["anomaly"]

# 6. Tampilkan hasil anomali
anomalies = df[df["anomaly"] == -1]
print(f"\n🚨 Jumlah data anomali terdeteksi: {len(anomalies)}")
print(anomalies[["timestamp", "temperature", "humidity", "ldr"]])

# 7. Tentukan ambang batas yang menunjukkan potensi kebakaran
def check_fire_risk(row):
    return (
        row["temperature"] > 45 and     # suhu tinggi
        row["humidity"] < 30 and        # kelembaban rendah
        row["ldr"] < 300 and            # cahaya tinggi (indikasi api)
        row["motion"] == 1              # ada gerakan (bisa manusia/lainnya)
    )

# 8. Tambahkan kolom prediksi kebakaran
df["fire_risk"] = df.apply(check_fire_risk, axis=1)

# 9. Tampilkan jika ada potensi kebakaran
fire_candidates = df[df["fire_risk"] == True]

if not fire_candidates.empty:
    latest = fire_candidates.iloc[-1]
    estimate_time = latest["timestamp"] + pd.Timedelta(hours=1)
    print("\n🔥 Kebakaran mungkin terjadi!")
    print(f"Estimasi waktu: {estimate_time}")
    print(latest[["timestamp", "temperature", "humidity", "ldr", "motion"]])
else:
    print("\n✅ Tidak ada indikasi kebakaran saat ini.")