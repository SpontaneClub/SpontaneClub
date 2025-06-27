import streamlit as st
import pandas as pd
from datetime import date
from PIL import Image
import base64
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ======== KONEKSI GOOGLE SHEETS via Secrets ========
def connect_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("SpontaneClubData")
    return {
        "kas": sheet.worksheet("kas_data"),
        "agenda": sheet.worksheet("agenda_data"),
        "struktur": sheet.worksheet("struktur_data")
    }

sheets = connect_gsheet()

# ======== FUNGSI UNTUK GOOGLE SHEETS ========
def tambah_kas(jenis, detail, jumlah, tanggal):
    sheets["kas"].append_row([tanggal, jenis, detail, jumlah])

def tambah_agenda(tanggal, kegiatan, foto):
    foto_nama = foto.name if foto else ""
    sheets["agenda"].append_row([tanggal, kegiatan, foto_nama])

def update_struktur(jabatan, nama):
    sheet = sheets["struktur"]
    data = sheet.get_all_records()
    sheet.clear()
    sheet.append_row(["Jabatan", "Nama"])
    updated = False
    for row in data:
        if row["Jabatan"] != jabatan:
            sheet.append_row([row["Jabatan"], row["Nama"]])
        else:
            sheet.append_row([jabatan, nama])
            updated = True
    if not updated:
        sheet.append_row([jabatan, nama])

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
st.title("⚽ Spontane Club Management")
menu = st.sidebar.radio("Menu", [
    "Pemasukan", "Pengeluaran", "Riwayat Kas",
    "Input Agenda", "Agenda", "Struktural"
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
    df = pd.DataFrame(sheets["kas"].get_all_records())
    if df.empty:
        st.info("Belum ada data kas.")
    else:
        df['Jumlah'] = df['Jumlah'].astype(int)
        keyword = st.text_input("Cari Nama/Detail")
        filtered = df[df['Detail'].str.contains(keyword, case=False)] if keyword else df
        pemasukan = filtered[filtered['Jenis'] == 'Pemasukan']['Jumlah'].sum()
        pengeluaran = filtered[filtered['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
        saldo = pemasukan - pengeluaran
        st.write(f"💰 Total Pemasukan: Rp {pemasukan:,}")
        st.write(f"📤 Total Pengeluaran: Rp {pengeluaran:,}")
        st.write(f"📦 Saldo: Rp {saldo:,}")
        st.dataframe(filtered)

elif menu == "Agenda":
    st.subheader("📅 Riwayat Agenda Kegiatan")
    data = sheets["agenda"].get_all_records()
    if not data:
        st.info("Belum ada data agenda.")
    else:
        for row in data:
            st.markdown(f"### 📌 {row['Kegiatan']}")
            st.markdown(f"🗓️ Tanggal: {row['Tanggal']}")
            if row['Foto']:
                st.markdown(f"🖼️ Foto: {row['Foto']}")
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
    data = sheets["struktur"].get_all_records()
    for row in data:
        st.markdown(f"- **{row['Jabatan']}**: {row['Nama']}")
    if st.session_state['user'] == "admin":
        st.markdown("---")
        st.markdown("### ✏️ Edit Struktur Organisasi")
        jabatan = st.selectbox("Pilih Jabatan", ["Ketua", "Penasehat Hukum", "Bendahara"])
        nama_baru = st.text_input("Nama Baru")
        if st.button("Simpan Perubahan") and nama_baru:
            update_struktur(jabatan, nama_baru)
            st.success(f"Struktur '{jabatan}' berhasil diperbarui.")
