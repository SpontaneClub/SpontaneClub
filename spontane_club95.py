import streamlit as st
import pandas as pd
import os
from datetime import date
from PIL import Image
import base64

# ======== KONFIGURASI HALAMAN ========
st.set_page_config(page_title="Spontan Club", layout="centered")

# ======== KONFIGURASI FILE & FOLDER ========
KAS_FILE = 'kas_data.csv'
SPARING_FILE = 'sparing_data.csv'
AGENDA_FILE = 'agenda_data.csv'
STRUKTUR_FILE = 'struktur_data.csv'
PHOTO_FOLDER = 'sparing_photos'
LOGO_IMAGE = 'spontane_club.jpg'

os.makedirs(PHOTO_FOLDER, exist_ok=True)

# ======== SETUP CSV ========
def init_csv(filename, columns):
    if not os.path.exists(filename):
        df = pd.DataFrame(columns=columns)
        df.to_csv(filename, index=False)

init_csv(KAS_FILE, ["Tanggal", "Jenis", "Keterangan", "Jumlah"])
init_csv(SPARING_FILE, ["Tanggal", "Lawan", "Skor", "Foto"])
init_csv(AGENDA_FILE, ["Tanggal", "Kegiatan", "Foto"])
init_csv(STRUKTUR_FILE, ["Jabatan", "Nama"])

# ======== HEADER LOGO & NAMA TIM ========
if os.path.exists(LOGO_IMAGE):
    with open(LOGO_IMAGE, "rb") as img_file:
        logo_data = base64.b64encode(img_file.read()).decode()
        st.markdown(
            f"""
            <div style='text-align: center; margin-bottom: 1rem;'>
                <img src='data:image/png;base64,{logo_data}' style='width:100px; margin-bottom: 10px;' />
                <h1 style='color: #1f2937; font-size: 28px;'>SPONTAN CLUB</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

# ======== LOGIN ========
st.sidebar.title("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_btn = st.sidebar.button("Login")

if login_btn:
    if username == "admin" and password == "'Spontan1995":
        st.session_state['user'] = "admin"
        st.sidebar.success("Login sebagai Admin")
    else:
        st.sidebar.warning("Login gagal")

if 'user' not in st.session_state:
    if st.sidebar.button("Lanjut sebagai Tamu"):
        st.session_state['user'] = "viewer"
        st.sidebar.info("Masuk sebagai Tamu (melihat saja)")

if 'user' not in st.session_state:
    st.stop()

# ======== MENU ========
st.title("⚽ Spontan Club Management")
if st.session_state['user'] == "admin":
    menu = st.sidebar.radio("Menu", ["Pemasukan", "Pengeluaran", "Riwayat Kas", "Input Sparing", "History Sparing", "Input Agenda", "Agenda", "Struktural"])
else:
    menu = st.sidebar.radio("Menu", ["Riwayat Kas", "History Sparing", "Agenda", "Struktural"])

# ======== FUNGSI TAMBAHAN ========
def tambah_kas(jenis, keterangan, jumlah):
    df = pd.read_csv(KAS_FILE)
    data = {
        "Tanggal": date.today().strftime("%Y-%m-%d"),
        "Jenis": jenis,
        "Keterangan": keterangan,
        "Jumlah": jumlah
    }
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(KAS_FILE, index=False)

def tambah_sparing(tanggal, lawan, skor, foto):
    filename = None
    if foto is not None:
        filename = os.path.join(PHOTO_FOLDER, foto.name)
        with open(filename, "wb") as f:
            f.write(foto.read())
    df = pd.read_csv(SPARING_FILE)
    data = {
        "Tanggal": tanggal,
        "Lawan": lawan,
        "Skor": skor,
        "Foto": filename
    }
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(SPARING_FILE, index=False)

def tambah_agenda(tanggal, kegiatan, foto):
    filename = None
    if foto is not None:
        filename = os.path.join(PHOTO_FOLDER, foto.name)
        with open(filename, "wb") as f:
            f.write(foto.read())
    df = pd.read_csv(AGENDA_FILE)
    data = {
        "Tanggal": tanggal,
        "Kegiatan": kegiatan,
        "Foto": filename
    }
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(AGENDA_FILE, index=False)

def update_struktur(jabatan, nama):
    df = pd.read_csv(STRUKTUR_FILE)
    df = df[df['Jabatan'] != jabatan]  # hapus yang lama
    df = pd.concat([df, pd.DataFrame([{"Jabatan": jabatan, "Nama": nama}])], ignore_index=True)
    df.to_csv(STRUKTUR_FILE, index=False)

# ======== FITUR: STRUKTURAL ========
if menu == "Struktural":
    st.subheader("👥 Struktur Organisasi Spontan Club")
    df = pd.read_csv(STRUKTUR_FILE)
    for _, row in df.iterrows():
        st.markdown(f"- **{row['Jabatan']}**: {row['Nama']}")

    if st.session_state['user'] == 'admin':
        st.markdown("---")
        st.markdown("### ✏️ Edit Struktur Organisasi")
        jabatan = st.selectbox("Pilih Jabatan", ["Ketua", "Penasehat Hukum", "Bendahara"])
        nama_baru = st.text_input("Nama Baru")
        if st.button("Simpan Perubahan"):
            if nama_baru:
                update_struktur(jabatan, nama_baru)
                st.success(f"Struktur '{jabatan}' berhasil diperbarui menjadi {nama_baru}.")

# ======== FITUR: INPUT AGENDA ========
if menu == "Input Agenda" and st.session_state['user'] == "admin":
    st.subheader("📝 Input Agenda Kegiatan")
    tanggal = st.date_input("Tanggal", value=date.today())
    kegiatan = st.text_input("Kegiatan")
    foto = st.file_uploader("Upload Foto Bersama", type=["jpg", "png"])
    if st.button("Simpan Agenda"):
        if kegiatan:
            tambah_agenda(tanggal.strftime("%Y-%m-%d"), kegiatan, foto)
            st.success("Agenda berhasil disimpan!")

# ======== FITUR: AGENDA ========
if menu == "Agenda":
    st.subheader("📅 Riwayat Agenda Kegiatan")
    df = pd.read_csv(AGENDA_FILE)
    if df.empty:
        st.info("Belum ada data agenda.")
    else:
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        for _, row in df.iterrows():
            st.markdown(f"### 📌 {row['Tanggal'].date()} - {row['Kegiatan']}")
            if pd.notna(row['Foto']) and os.path.exists(row['Foto']):
                st.image(row['Foto'], width=300)
            st.markdown("---")
