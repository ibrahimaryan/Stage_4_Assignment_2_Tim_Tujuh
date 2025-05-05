import streamlit as st

st.set_page_config(page_title="Tentang Tim", layout="wide")

st.title("ℹ️ About")
st.markdown("### Assignment 3 SIC 6 - UNI415 Tim Tujuh")
st.write("""
Ini merupakan mini projek studi kasus **alarm kebakaran** yang memadukan **IoT** dengan **AI**.  
Kasus ini terinspirasi dari sistem **alarm kebakaran di hutan** yang bertujuan mendeteksi dan mengirimkan data secara real-time melalui sensor ke server.

#### 👥 Anggota Tim dan Pembagian Tugas:
1. **Aldo Ramadhana** : Membuat middleware dan database mongodbatlas
2. **Ammar Luqman Arifin** : Menentukan alur pengiriman data hingga tampil di dashboard
3. **Danu Alamsyah Putra** : Merangkai hardware IoT dan membuat kodenya
4. **Ibrahim Aryan Faridzi** : Membuat dashboard ubidots, membuat dahsboard streamlit, dan implementasi AI
""")