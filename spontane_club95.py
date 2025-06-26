import streamlit as st
import pandas as pd
import os
from datetime import date
from PIL import Image
import base64

# ======== KONFIGURASI HALAMAN ========
st.set_page_config(page_title="Spontane Club", layout="centered")

# ======== KONFIGURASI FILE & FOLDER ========
KAS_FILE = 'kas_data.csv'
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
st.title("⚽ Spontane Club Management")
if st.session_state['user'] == "admin":
    menu = st.sidebar.radio("Menu", ["Pemasukan", "Pengeluaran", "Riwayat Kas", "Input Agenda", "Agenda", "Struktural"])
else:
    menu = st.sidebar.radio("Menu", ["Riwayat Kas", "Agenda", "Struktural"])

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

# ======== FITUR: PEMASUKAN ========
if menu == "Pemasukan" and st.session_state['user'] == "admin":
    st.subheader("🟢 Input Pemasukan")
    ket = st.text_input("Keterangan")
    jml = st.number_input("Jumlah", min_value=0)
    if st.button("Simpan Pemasukan"):
        if ket and jml > 0:
            tambah_kas("Pemasukan", ket, jml)
            st.success("Pemasukan berhasil disimpan!")

# ======== FITUR: PENGELUARAN ========
if menu == "Pengeluaran" and st.session_state['user'] == "admin":
    st.subheader("🔴 Input Pengeluaran")
    ket = st.text_input("Keterangan")
    jml = st.number_input("Jumlah", min_value=0)
    if st.button("Simpan Pengeluaran"):
        if ket and jml > 0:
            tambah_kas("Pengeluaran", ket, jml)
            st.success("Pengeluaran berhasil disimpan!")

# ======== FITUR: RIWAYAT KAS ========
if menu == "Riwayat Kas":
    st.subheader("📊 Riwayat Uang Kas")
    df = pd.read_csv(KAS_FILE)

    if df.empty:
        st.info("Belum ada data kas.")
    else:
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        df['Jumlah'] = df['Jumlah'].astype(int)

        col1, col2 = st.columns(2)
        with col1:
            tgl_mulai = st.date_input("Dari Tanggal", df['Tanggal'].min().date())
        with col2:
            tgl_akhir = st.date_input("Sampai Tanggal", df['Tanggal'].max().date())

        keyword = st.text_input("Cari Keterangan")

        filtered = df[(df['Tanggal'] >= pd.to_datetime(tgl_mulai)) &
                      (df['Tanggal'] <= pd.to_datetime(tgl_akhir))]
        if keyword:
            filtered = filtered[filtered['Keterangan'].str.contains(keyword, case=False)]

        pemasukan = filtered[filtered['Jenis'] == 'Pemasukan']['Jumlah'].sum()
        pengeluaran = filtered[filtered['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
        saldo = pemasukan - pengeluaran

        st.write(f"💰 Total Pemasukan: Rp {pemasukan:,}")
        st.write(f"📤 Total Pengeluaran: Rp {pengeluaran:,}")
        st.write(f"📦 Saldo: Rp {saldo:,}")
        st.dataframe(filtered)

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
