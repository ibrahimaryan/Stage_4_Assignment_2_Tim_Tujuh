# Assignment 3 - UNI415 Tim Tujuh
Kode sederhana esp32 melakukan collect data sensor mengirim ke dashboard ubidots [Dashboard](https://stem.ubidots.com/app/dashboards/public/dashboard/lvaP28Nk53BCHKAnCaAvYak4ZQhuH_SsENEs8u3-PTM?navbar=true&contextbar=false) dan mongodb atlas, lalu menampilkan dashboard menggunakan streamlit yang datanya akan dianalisa oleh gemini ai, pada streamlit juga menyediakan chatbot secara terpisah untuk melakukan prompt pertanyaan

## Tutorial running kode :
- Pastikan laptop dan esp32 berada di jaringan internet yang sama
- Ubah bagian ini di esp32.py menjadi ip laptop Anda :
> SERVER_URL =  "http://172.90.1.26:5000/sensor"
- Ubah bagian ini di esp32.py :
> SSID = "Pixel_3770"   # Ganti dengan nama WiFi

> PASSWORD = "adamhawa"  # Ganti dengan password WiFi
- Pastikan sudah melakukan install depedensi seperti di requirements.txt
- Jalankan file **server.py**
> python server.py
- Jika berhasil akan menampilkan output
> Running on http://0.0.0.0:5000 (Press CTRL+C to quit)
- Jalankan esp32 setelah server.py berjalan
- Untuk menjalankan streamlit secara lokal
> streamlit run dashboard.py
- Atau bisa mengunjungi [link berikut](https://timtujuhassignment3-em4oqdkqcdtkfpf8skflxr.streamlit.app) untuk menggunakan streamlit melalui streamlit cloud
- Monitoring melalui [ubidots](https://stem.ubidots.com/app/dashboards/public/dashboard/lvaP28Nk53BCHKAnCaAvYak4ZQhuH_SsENEs8u3-PTM?navbar=true&contextbar=false)