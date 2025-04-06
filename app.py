import streamlit as st
import pandas as pd
import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Ayarlar
st.set_page_config(page_title="CYHELP", page_icon="🧠")
st.markdown("<h1 style='text-align: center;'>🧠 CYHELP | Yapay Zeka Destekli VAVA İş Akış Asistanı</h1>", unsafe_allow_html=True)

# Excel dosyalarını yükle
df = pd.read_excel("veri.xlsx")
log_file_path = "soru_loglari.xlsx"

# Google Sheet Ayarı
sheet_id = "1xkLogLi6AD5Z2TILjGhnNIVecKT608LbQpaZrORV6yI"
sheet_name = "Sayfa1"

# Kullanıcı girişi ve soru
soru = st.text_input("📝 Sorunuzu yazın (örnek: sistem dondu, giriş yapamıyorum...):")
kullanici = st.text_input("👤 Kullanıcı adınız (isteğe bağlı):")

# Anahtar kelime eşleştirme
def yakala(cumle):
    cumle = cumle.lower()
    for kelime in df["Anahtar Kelime"].dropna().unique():
        if kelime.lower() in cumle:
            return kelime
    return None

def senaryo_bul(kelime):
    return df[df["Anahtar Kelime"].str.lower() == kelime.lower()]

def senaryo_goster(row):
    st.subheader(f"📌 {row['Senaryo']}")
    st.markdown(f"**🔎 Açıklama:** {row['Açıklama']}")
    st.markdown(f"**🛠️ Çözüm:** {row['Çözüm']}")
    st.markdown(f"**👤 Sorumlu:** {row['Sorumlu']}")
    if pd.notna(row["Görsel"]) and row["Görsel"] != "":
        image_path = os.path.join("images", row["Görsel"])
        if os.path.exists(image_path):
            st.image(image_path, caption=row["Senaryo"], use_column_width=True)
        else:
            st.warning(f"⚠️ Hata ile ilgili görsel bulunamadı")

# Logları yaz
def log_yaz(soru, durum, kullanici):
    zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    yeni = pd.DataFrame([{
        "Tarih": zaman,
        "Soru": soru,
        "Durum": durum,
        "Kullanıcı": kullanici if kullanici else "-"
    }])
    # Yerel log
    if os.path.exists(log_file_path):
        mevcut = pd.read_excel(log_file_path)
        log_df = pd.concat([mevcut, yeni], ignore_index=True)
    else:
        log_df = yeni
    log_df.to_excel(log_file_path, index=False)

    # Google Sheet log
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        sheet.append_row([zaman, soru, durum, kullanici if kullanici else "-"])
    except Exception as e:
        st.warning(f"⚠️ Google Sheet log hatası: {e}")

# Admin panel girişi
if soru == "cyadminacil":
    user = st.text_input("👤 Kullanıcı Adı:")
    password = st.text_input("🔐 Şifre:", type="password")
    if user == "cmyvava" and password == "12345":
        st.success("✅ Giriş başarılı. Loglar aşağıda:")

        if os.path.exists(log_file_path):
            logs = pd.read_excel(log_file_path)
            st.dataframe(logs)
            st.download_button("📥 Excel olarak indir", data=logs.to_excel(index=False), file_name="soru_loglari.xlsx")

            if st.button("🧹 Logları Sıfırla"):
                os.remove(log_file_path)
                st.warning("📁 Log dosyası sıfırlandı.")
        else:
            st.info("📂 Log dosyası henüz oluşmadı.")
    else:
        st.warning("🔒 Giriş başarısız")
    st.stop()

# Soru varsa işle
if soru:
    bulunan = yakala(soru)
    if bulunan:
        senaryolar = senaryo_bul(bulunan)
        if not senaryolar.empty:
            st.info(f"🧠 '{bulunan}' ile ilgili {len(senaryolar)} çözüm bulundu:")
            secim = st.selectbox("Lütfen neyi kastettiğinizi seçin:", senaryolar["Senaryo"].tolist())
            secilen = senaryolar[senaryolar["Senaryo"] == secim]
            senaryo_goster(secilen.iloc[0])
            log_yaz(soru, "Eşleşme bulundu", kullanici)
        else:
            st.warning("⚠️ Eşleşen anahtar kelime bulundu ama senaryo bilgisi eksik.")
            log_yaz(soru, "Anahtar eşleşti ama senaryo yok", kullanici)
    else:
        st.warning("🤖 Bu soruya dair kayıtlı bir bilgi bulunamadı.")
        log_yaz(soru, "Eşleşme bulunamadı", kullanici)
