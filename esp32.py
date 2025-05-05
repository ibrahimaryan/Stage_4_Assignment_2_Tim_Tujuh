from machine import Pin, ADC, PWM
import time
import urequests as requests
import dht
import network

# Inisialisasi sensor dan komponen
ldr = ADC(Pin(35))  # LDR di GPIO35
ldr.atten(ADC.ATTN_11DB)
ldr.width(ADC.WIDTH_10BIT)

dht_pin = Pin(15)  # DHT11 di GPIO15
sensor_dht = dht.DHT11(dht_pin)

pir = Pin(4, Pin.IN)  # PIR di GPIO4

# Inisialisasi buzzer di GPIO21
buzzer = PWM(Pin(21), duty=0)

# Konfigurasi Wi-Fi
SSID = "OPPOA5Pro"
PASSWORD = "rgnk8263"

# Konfigurasi Ubidots
TOKEN = "BBUS-A33lRaUTEicWD2INjCihT8n0yODbOp"
DEVICE_LABEL = "esp32-sic6-assignment3"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("[INFO] Menghubungkan ke Wi-Fi...")
        wlan.connect(SSID, PASSWORD)
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        print("[INFO] Terhubung ke Wi-Fi:", wlan.ifconfig())
    else:
        print("[ERROR] Gagal terhubung ke Wi-Fi!")

def read_sensors():
    try:
        sensor_dht.measure()
        temperature = sensor_dht.temperature()
        humidity = sensor_dht.humidity()
        ldr_value = ldr.read()
    except Exception as e:
        print("[ERROR] Gagal membaca sensor DHT11:", e)
        temperature, humidity, ldr_value = None, None, None

    motion = pir.value()
    
    return temperature, humidity, motion, ldr_value

def build_payload(temperature, humidity, motion, ldr_value):
    return {
        "temperature": temperature,
        "humidity": humidity,
        "ldr": ldr_value,
        "motion": motion
    }

def post_request(payload):
    url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    attempts = 0
    status = 400
    while status >= 400 and attempts < 5:
        try:
            print(f"[DEBUG] Mengirim data ke {url}, Percobaan {attempts+1}")
            req = requests.post(url, headers=headers, json=payload)
            status = req.status_code
            print(f"[DEBUG] Response Status: {status}")
            print(f"[DEBUG] Response Body: {req.text}")

            if status < 400:
                print("[INFO] Data berhasil dikirim ke Ubidots:", req.json())
                return True
            else:
                print(f"[WARNING] Gagal mengirim ke Ubidots, kode status: {status}")
        except Exception as e:
            print("[ERROR] Gagal mengirim ke Ubidots:", str(e))

        attempts += 1
        time.sleep(1)

    print("[ERROR] Gagal mengirim data ke Ubidots setelah 5 kali percobaan.")
    return False

def post_db(payload):
    SERVER_URL = "http://192.168.60.213:5000/sensor"
    headers = {"Content-Type": "application/json"}

    print("[DEBUG] Data yang dikirim ke server:", payload)

    try:
        response = requests.post(SERVER_URL, json=payload, headers=headers)
        json_data = response.json()

        print("[INFO] Respon Server:", json_data)

        # Periksa apakah anomaly adalah -1 dan nyalakan buzzer jika true
        if json_data.get("anomaly") == -1:
            print("🚨 Data anomali terdeteksi! Membunyikan buzzer...")
            buzzer.freq(1000)
            buzzer.duty(512)  # Nyalakan buzzer
            time.sleep(2)  # Biarkan buzzer menyala selama 2 detik
            buzzer.duty(0)  # Matikan buzzer
        else:
            buzzer.duty(0)  # Matikan buzzer jika tidak ada anomali

        response.close()
        return True
    except Exception as e:
        print("[ERROR] Gagal mengirim data:", str(e))
        return False

def main():
    temperature, humidity, motion, ldr_value = read_sensors()

    if temperature is None or humidity is None:
        print("[ERROR] Sensor DHT gagal, data tidak akan dikirim.")
        return

    payload = build_payload(temperature, humidity, motion, ldr_value)

    print("[INFO] Mengirim data ke Ubidots dan MongoDB...")
    post_request(payload)
    post_db(payload)

if __name__ == '__main__':
    connect_wifi()
    while True:
        main()
        time.sleep(8)