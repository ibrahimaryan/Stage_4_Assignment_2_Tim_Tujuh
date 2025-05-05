# dashboard.py
import streamlit as st
import pandas as pd
import pymongo
import altair as alt
from model.genai import get_response
from streamlit_autorefresh import st_autorefresh
from pymongo.server_api import ServerApi

# Koneksi ke MongoDB
client = pymongo.MongoClient("mongodb+srv://timtujuh:vV2WEXiqjSTmPevl@clustertimtujuh.8p34h.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTimTujuh", server_api=ServerApi('1'))
db = client["TimTujuhDatabase"]
collection = db["MySensorData"]

st.set_page_config(page_title="Dashboard Sensor ESP32", layout="wide")

st.title("📊 Dashboard Alarm Kebakaran - UNI415 Tim Tujuh")
st.markdown("Data suhu, kelembapan, LDR, dan gerakan dari MongoDB terbaru.")

@st.cache_data(ttl=8)
def get_sensor_data():
    try:
        # Mengambil data dari MongoDB
        data = list(collection.find({}, {"_id": 0}).sort("timestamp", -1))
        df = pd.DataFrame(data)

        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.sort_values(by='timestamp', inplace=True)
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = get_sensor_data()

if df.empty:
    st.warning("Belum ada data yang tersedia.")
    st.stop()

# ===== Ringkasan Data =====
latest = df.iloc[-1]
col1, col2, col3, col4 = st.columns(4)
col1.metric("🌡️ Suhu (°C)", f"{latest['temperature']} °C")
col2.metric("💧 Kelembapan (%)", f"{latest['humidity']} %")
col3.metric("☀️ LDR", f"{latest['ldr']}")
col4.metric("🚶 Gerakan", "Terdeteksi" if latest['motion'] == 1 else "Tidak Ada")

# ===== Status Potensi Kebakaran & Anomali =====
status_placeholder = st.empty()

if "anomaly" in latest and latest["anomaly"] == -1:
    status_text = "🚨 **Anomali Data!! Ada kebakaran!**"
    status_placeholder.error(status_text)
elif latest["temperature"] > 26 and latest["humidity"] < 90 and latest["ldr"] > 200:
    status_text = "🚨 **Siaga: Ada kebakaran!**"
    status_placeholder.error(status_text)
elif latest["temperature"] > 24 and latest["humidity"] < 95 and latest["ldr"] > 100:
    status_text = "⚠️ **Hati-hati: Potensi kebakaran**"
    status_placeholder.warning(status_text)
else:
    status_text = "✅ **Aman**"
    status_placeholder.success(status_text)

# ===== AI Prompt =====
auto_prompt = (
    "Berikut adalah data terbaru dari sistem pemantauan kebakaran hutan berbasis IoT:\n\n"
    f"- 🌡️ Suhu: {latest['temperature']} °C\n"
    f"- 💧 Kelembapan: {latest['humidity']} %\n"
    f"- ☀️ Intensitas cahaya (LDR): {latest['ldr']}\n"
    f"- 🚶 Deteksi Gerakan: {'Terdeteksi' if latest['motion'] == 1 else 'Tidak ada'}\n\n"
    "Analisislah kondisi ini dalam konteks potensi kebakaran hutan:\n"
    "- Apakah suhu dan kelembapan menunjukkan kondisi rawan kebakaran?\n"
    "- Bagaimana interpretasi nilai LDR terhadap intensitas cahaya yang mungkin menandakan api?\n"
    "- Apakah gerakan bisa menandakan aktivitas manusia atau binatang yang relevan?\n\n"
    "Buatlah kesimpulan ringkas mengenai tingkat risiko kebakaran saat ini dan rekomendasi jika perlu."
)

try:
    response = get_response(auto_prompt)
    st.markdown("### 🤖 Rangkuman kondisi berdasarkan AI")
    st.info(response)
except Exception as e:
    st.error(f"Gagal menghasilkan analisis AI: {e}")

# ===== Filter & Visualisasi =====
st.markdown("### 📈 Visualisasi Data Sensor")
time_range = st.selectbox("Pilih jangka waktu tampilan data:", ["24 Jam", "7 Hari", "30 Hari", "1 Tahun"])
now = pd.Timestamp.now()

if time_range == "24 Jam":
    df_filtered = df[df["timestamp"] >= now - pd.Timedelta(days=1)]
elif time_range == "7 Hari":
    df_filtered = df[df["timestamp"] >= now - pd.Timedelta(days=7)]
elif time_range == "30 Hari":
    df_filtered = df[df["timestamp"] >= now - pd.Timedelta(days=30)]
else:
    df_filtered = df.copy()

if time_range in ["7 Hari", "30 Hari", "1 Tahun"]:
    df_filtered = df_filtered.set_index("timestamp").resample("1H").mean().reset_index()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🌡️ Suhu (°C)")
    st.altair_chart(alt.Chart(df_filtered).mark_line(point=True).encode(
        x="timestamp:T", y=alt.Y("temperature:Q", title="Suhu (°C)"),
        tooltip=["timestamp", "temperature"]), use_container_width=True)

    st.subheader("🚶 Deteksi Gerakan")
    motion_df = df_filtered.copy()
    if "motion" in motion_df.columns:
        motion_df["motion"] = motion_df["motion"].fillna(0).astype(int)
    st.altair_chart(alt.Chart(motion_df).mark_bar().encode(
        x="timestamp:T",
        y=alt.Y("motion:Q", title="Gerakan"),
        color=alt.condition(
            alt.datum.motion == 1,
            alt.value("orangered"), alt.value("lightgray")
        ),
        tooltip=["timestamp", "motion"]
    ).properties(height=200), use_container_width=True)

with col2:
    st.subheader("💧 Kelembapan (%)")
    st.altair_chart(alt.Chart(df_filtered).mark_line(point=True).encode(
        x="timestamp:T", y=alt.Y("humidity:Q", title="Kelembapan (%)"),
        tooltip=["timestamp", "humidity"]), use_container_width=True)

    st.subheader("☀️ Intensitas Cahaya (LDR)")
    st.altair_chart(alt.Chart(df_filtered).mark_line(point=True).encode(
        x="timestamp:T", y=alt.Y("ldr:Q", title="Nilai LDR"),
        tooltip=["timestamp", "ldr"]), use_container_width=True)

st_autorefresh(interval=8000, key="data_refresh")
