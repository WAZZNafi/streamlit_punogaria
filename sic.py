import streamlit as st
import pandas as pd
import numpy as np
import requests
import cv2
from PIL import Image
from io import BytesIO
import time

# ========== Konfigurasi Awal ==========
st.set_page_config(page_title="PUNOGARIA", layout="centered")

st.title("🌿 PUNOGARIA: Sistem Penyiraman Otomatis dengan Sensor 🌱")
st.write("""
Simulasi penyiraman otomatis berdasarkan suhu, kelembapan, dan kondisi langit dari kamera ESP32-CAM.
Pompa akan **MENYALA** jika:
- Kelembapan tanah di bawah ambang batas
- ATAU suhu terlalu panas
- DAN langit **tidak mendung**
""")

# IP Kamera & ESP32 (ganti sesuai milikmu)
camera_url = "http://192.168.180.196/capture"
esp32_url = "http://192.168.180.203"  # Ganti sesuai IP ESP32 kamu

# ========== Fungsi Ambil Data Sensor dari ESP32 ==========
def ambil_data_dari_esp32():
    try:
        response = requests.get(esp32_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            suhu = data.get("temperature")
            kelembapan = data.get("humidity")
            return suhu, kelembapan
        else:
            st.warning(f"Gagal ambil data dari ESP32. Status code: {response.status_code}")
            return None, None
    except Exception as e:
        st.error(f"Error ambil data dari ESP32: {e}")
        return None, None

# ========== Fungsi Deteksi Cuaca dari Kamera ==========
def deteksi_langit_dari_kamera(url):
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content))
        img_np = np.array(img)

        tinggi, lebar, _ = img_np.shape
        potongan_langit = img_np[0:int(tinggi * 0.3), :, :]

        hsv = cv2.cvtColor(potongan_langit, cv2.COLOR_RGB2HSV)
        brightness = hsv[:, :, 2].mean()
        hue = hsv[:, :, 0].mean()
        saturation = hsv[:, :, 1].mean()

        if brightness > 180 and saturation < 60:
            return "Cerah ☀️"
        elif brightness > 100 and saturation < 100:
            return "Berawan ⛅"
        else:
            return "Mendung / Mau Hujan 🌧️"
    except Exception as e:
        return f"Gagal mendeteksi langit: {e}"

# ========== UI Elements ==========
batas_kelembapan = st.sidebar.slider("🔧 Batas Kelembapan (%)", 10, 100, 40)
mode = st.sidebar.radio("🔄 Pilih Mode", ["Otomatis", "Manual"])
data = pd.DataFrame(columns=["Suhu", "Kelembapan"])
metric_placeholder = st.empty()
status_placeholder = st.empty()
chart_placeholder = st.empty()
cuaca_placeholder = st.empty()
kamera_placeholder = st.empty()
progress_bar = st.progress(0)
waktu_placeholder = st.empty()
total_durasi = 20

# ========== Session State ==========
if "status_pompa_manual" not in st.session_state:
    st.session_state.status_pompa_manual = "MATI 🔴"
if "pompa_menyala" not in st.session_state:
    st.session_state.pompa_menyala = False

# ========== Mode Otomatis ==========
if mode == "Otomatis":
    if st.button("🚀 Mulai Simulasi Otomatis"):
        for i in range(total_durasi):
            suhu, kelembapan = ambil_data_dari_esp32()
            if suhu is None or kelembapan is None:
                suhu = np.random.uniform(20, 40)
                kelembapan = np.random.uniform(10, 100)

            kondisi_langit = deteksi_langit_dari_kamera(camera_url)

            new_row = pd.DataFrame({"Suhu": [suhu], "Kelembapan": [kelembapan]})
            data = pd.concat([data, new_row], ignore_index=True)

            alasan = []
            if kelembapan < batas_kelembapan:
                alasan.append("kelembapan rendah")
            if suhu > 35:
                alasan.append("suhu tinggi")

            cuaca_buruk = "Mendung" in kondisi_langit or "Hujan" in kondisi_langit
            if alasan and not cuaca_buruk:
                status_pompa = "MENYALA 🟢"
                warna = "green"
                penyebab = ", ".join(alasan)
            elif cuaca_buruk:
                status_pompa = "MATI 🔴"
                warna = "red"
                penyebab = "cuaca buruk (mendung/hujan)"
            else:
                status_pompa = "MATI 🔴"
                warna = "red"
                penyebab = "kondisi normal"

            with metric_placeholder.container():
                st.metric("🌡️ Suhu Tanah (°C)", f"{suhu:.2f}")
                st.metric("💧 Kelembapan Tanah (%)", f"{kelembapan:.2f}")

            with status_placeholder.container():
                st.markdown(f"""
                ### Status Pompa: <span style='color:{warna}'>{status_pompa}</span>  
                **Penyebab:** {penyebab}
                """, unsafe_allow_html=True)

            with chart_placeholder.container():
                st.line_chart(data)

            with cuaca_placeholder.container():
                st.write(f"🌤️ **Kondisi Langit**: {kondisi_langit}")

            try:
                response = requests.get(camera_url, timeout=5)
                img = Image.open(BytesIO(response.content))
                kamera_placeholder.image(img, caption="Tampilan Langit", use_container_width=True)
            except:
                kamera_placeholder.warning("Gagal memuat gambar dari kamera.")

            progress = int(((i + 1) / total_durasi) * 100)
            progress_bar.progress(min(progress, 100))
            waktu_placeholder.write(f"⏱️ Waktu Simulasi: {i+1} detik")
            time.sleep(1)

# ========== Mode Manual ==========
elif mode == "Manual":
    st.write("💡 Mode Manual: Anda dapat mengontrol pompa secara langsung.")

    col1, col2 = st.columns(2)
    if not st.session_state.pompa_menyala:
        with col1:
            if st.button("🌱 Nyalakan Pompa"):
                st.session_state.status_pompa_manual = "MENYALA 🟢"
                st.session_state.pompa_menyala = True
    else:
        with col2:
            if st.button("🛑 Matikan Pompa"):
                st.session_state.status_pompa_manual = "MATI 🔴"
                st.session_state.pompa_menyala = False

    with status_placeholder.container():
        warna = "green" if st.session_state.status_pompa_manual == "MENYALA 🟢" else "red"
        st.markdown(f"""
        ### Status Pompa: <span style='color:{warna}'>{st.session_state.status_pompa_manual}</span>  
        """, unsafe_allow_html=True)

    with metric_placeholder.container():
        suhu, kelembapan = ambil_data_dari_esp32()
        suhu_text = f"{suhu:.2f}" if suhu else "0.00"
        kelembapan_text = f"{kelembapan:.2f}" if kelembapan else "0.00"
        st.metric("🌡️ Suhu Tanah (°C)", suhu_text)
        st.metric("💧 Kelembapan Tanah (%)", kelembapan_text)

# ========== Reset ==========
progress_bar.progress(0)
waktu_placeholder.write("⏱️ Waktu Simulasi: 0 detik")
