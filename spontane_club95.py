import streamlit as st
import pandas as pd
from datetime import date
from PIL import Image
import base64
import os
import mysql.connector

# ======== KONEKSI KE MYSQL LOCAL (XAMPP) ========
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )

# ======== FUNGSI MYSQL ========
def tambah_kas(jenis, detail, jumlah, tanggal):
    conn = get_connection()
    cursor = conn.cursor()
    query = "INSERT INTO kas_data (tanggal, jenis, detail, jumlah) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (tanggal, jenis, detail, jumlah))
    conn.commit()
    cursor.close()


def tambah_agenda(tanggal, kegiatan, foto):
    conn = get_connection()
    cursor = conn.cursor()
    foto_nama = foto.name if foto else ""
    query = "INSERT INTO agenda_data (tanggal, kegiatan, foto) VALUES (%s, %s, %s)"
    cursor.execute(query, (tanggal, kegiatan, foto_nama))
    conn.commit()
    cursor.close()


def update_struktur(jabatan, nama):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM struktur_data WHERE jabatan = %s", (jabatan,))
    cursor.execute("INSERT INTO struktur_data (jabatan, nama) VALUES (%s, %s)", (jabatan, nama))
    conn.commit()
    cursor.close()


def simpan_anggota(nama, nomor_hp):
    conn = get_connection()
    cursor = conn.cursor()
    query = "INSERT INTO anggota_data (nama, nomor_hp) VALUES (%s, %s)"
    cursor.execute(query, (nama, nomor_hp))
    conn.commit()
    cursor.close()

# ======== LOGO ========
LOGO_IMAGE = 'spontane_club.jpg'
if os.path.exists(LOGO_IMAGE):
    with open(LOGO_IMAGE, "rb") as img_file:
        logo_data = base64.b64encode(img_file.read()).decode()
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 1rem;'>
            <img src='data:image/png;base64,{logo_data}' style='width:100px; margin-bottom: 10px;' />
            <h1 style='color: #1f2937; font-size: 28px;'>SPONTANE CLUB</h1>
        </div>
        """, unsafe_allow_html=True)

# ======== LOGIN ========
st.sidebar.title("Login")
if 'user' not in st.session_state:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "admin" and password == "'Spontan1995":
            st.session_state['user'] = "admin"
            st.sidebar.success("Login sebagai Admin")
        else:
            st.sidebar.warning("Login gagal")
    if st.sidebar.button("Lanjut sebagai Tamu"):
        st.session_state['user'] = "viewer"
        st.sidebar.info("Masuk sebagai Tamu (melihat saja)")

if st.session_state.get('user') == 'admin':
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.stop()

if 'user' not in st.session_state:
    st.stop()

# ======== MENU ========
st.title("🏀 Spontane Club Management")
menu = st.sidebar.radio("Menu", [
    "Pemasukan", "Pengeluaran", "Riwayat Kas",
    "Input Agenda", "Agenda", "Struktural", "Input Anggota"
] if st.session_state['user'] == "admin" else ["Riwayat Kas", "Agenda", "Struktural"])

# ======== FITUR ========
if menu == "Pemasukan":
    st.subheader("🟢 Input Pemasukan")
    tanggal = st.date_input("Tanggal", value=date.today())
    detail = st.text_input("Nama Pembayar")
    jml = st.number_input("Jumlah", min_value=0)
    if st.button("Simpan Pemasukan") and detail and jml > 0:
        tambah_kas("Pemasukan", detail, jml, tanggal.strftime("%Y-%m-%d"))
        st.success("Pemasukan berhasil disimpan!")

elif menu == "Pengeluaran":
    st.subheader("🔴 Input Pengeluaran")
    tanggal = st.date_input("Tanggal", value=date.today())
    detail = st.text_input("Nama Penerima/Detail")
    jml = st.number_input("Jumlah", min_value=0)
    if st.button("Simpan Pengeluaran") and detail and jml > 0:
        tambah_kas("Pengeluaran", detail, jml, tanggal.strftime("%Y-%m-%d"))
        st.success("Pengeluaran berhasil disimpan!")

elif menu == "Riwayat Kas":
    st.subheader("📊 Riwayat Uang Kas")
    conn = get_connection()
    df = pd.read_sql("SELECT tanggal, jenis, detail, jumlah FROM kas_data", conn)
    if df.empty:
        st.info("Belum ada data kas.")
    else:
        df['Jumlah'] = df['jumlah'].astype(int)
        keyword = st.text_input("Cari Nama/Detail")
        filtered = df[df['detail'].str.contains(keyword, case=False)] if keyword else df
        pemasukan = filtered[filtered['jenis'] == 'Pemasukan']['jumlah'].sum()
        pengeluaran = filtered[filtered['jenis'] == 'Pengeluaran']['jumlah'].sum()
        saldo = pemasukan - pengeluaran
        st.write(f"💰 Total Pemasukan: Rp {pemasukan:,}")
        st.write(f"🛄 Total Pengeluaran: Rp {pengeluaran:,}")
        st.write(f"🛆 Saldo: Rp {saldo:,}")
        st.dataframe(filtered)

elif menu == "Agenda":
    st.subheader("🗕️ Riwayat Agenda Kegiatan")
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM agenda_data", conn)
    if df.empty:
        st.info("Belum ada data agenda.")
    else:
        for _, row in df.iterrows():
            st.markdown(f"### 📌 {row['kegiatan']}")
            st.markdown(f"🗓️ Tanggal: {row['tanggal']}")
            if row['foto']:
                st.markdown(f"🖼️ Foto: {row['foto']}")
            st.markdown("---")

elif menu == "Input Agenda":
    st.subheader("📝 Input Agenda Kegiatan")
    tanggal = st.date_input("Tanggal", value=date.today())
    kegiatan = st.text_input("Kegiatan")
    foto = st.file_uploader("Upload Foto Bersama", type=["jpg", "png"])
    if st.button("Simpan Agenda") and kegiatan:
        tambah_agenda(tanggal.strftime("%Y-%m-%d"), kegiatan, foto)
        st.success("Agenda berhasil disimpan!")

elif menu == "Struktural":
    st.subheader("👥 Struktur Organisasi Spontane Club")
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM struktur_data", conn)
    for _, row in df.iterrows():
        st.markdown(f"- **{row['jabatan']}**: {row['nama']}")
    if st.session_state['user'] == "admin":
        st.markdown("---")
        st.markdown("### ✏️ Edit Struktur Organisasi")
        jabatan = st.selectbox("Pilih Jabatan", ["Ketua", "Penasehat Hukum", "Bendahara"])
        nama_baru = st.text_input("Nama Baru")
        if st.button("Simpan Perubahan") and nama_baru:
            update_struktur(jabatan, nama_baru)
            st.success(f"Struktur '{jabatan}' berhasil diperbarui.")

elif menu == "Input Anggota":
    st.subheader("📇 Input Data Anggota")
    nama = st.text_input("Nama Lengkap")
    nomor = st.text_input("Nomor HP")
    if st.button("Simpan"):
        if nama and nomor:
            simpan_anggota(nama, nomor)
            st.success(f"Data '{nama}' berhasil disimpan!")
        else:
            st.warning("Mohon isi semua kolom.")

    st.markdown("### 📋 Daftar Anggota")
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM anggota_data", conn)
    st.dataframe(df)
