import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Sayfa ayarı
st.set_page_config(page_title="CYHELP", page_icon="🧠")
st.title("🔧 CYHELP | Yapay Zeka Destekli VAVA İş Akış Asistanı")

# Ana veriler
df = pd.read_excel("veri.xlsx")
stop_words = ["ben", "bir", "bu", "şu", "ve", "ile", "de", "da", "ama", "çok", "neden", "nasıl", "şey", "gibi", "ki"]

es_anlamli = {
    "dondu": ["kitlendi", "takıldı", "çöktü", "donuyor", "kasma"],
    "giriş": ["login", "şifre", "oturum", "giremiyorum"],
    "ruhsat": ["belge", "noter evrağı", "vesika"],
    "çalışmıyor": ["açılmıyor", "başlamıyor", "görünmüyor"]
}

# Google Sheet bağlantısı
def google_log_yaz(log):
    try:
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/spreadsheets",
                 "https://www.googleapis.com/auth/drive.file",
                 "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1xkLogLi6AD5Z2TILjGhnNIVecKT608LbQpaZrORV6yI").sheet1
        sheet.append_row([log["Tarih"], log["Kullanıcı"], log["Soru"], log["Durum"]])
    except Exception as e:
        print("Google Sheet log hatası:", e)

# Log yazma
def logla(soru, kullanici, durum="Eşleşme bulunamadı"):
    tarih = (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
    yeni_log = {
        "Tarih": tarih,
        "Kullanıcı": kullanici if kullanici else "-",
        "Soru": soru,
        "Durum": durum
    }

    # Excel'e yaz
    log_yolu = "soru_loglari.xlsx"
    try:
        mevcut = pd.read_excel(log_yolu)
        log_df = pd.concat([mevcut, pd.DataFrame([yeni_log])], ignore_index=True)
    except:
        log_df = pd.DataFrame([yeni_log])
    log_df.to_excel(log_yolu, index=False)

    # Google Sheet'e yaz
    google_log_yaz(yeni_log)

# Anahtar kelime yakalama
def anahtar_kelime_bul(soru):
    kelimeler = re.findall(r'\b\w+\b', soru.lower())
    anlamli = [k for k in kelimeler if k not in stop_words]
    for k in anlamli:
        for ak in df["Anahtar Kelime"].unique():
            if k in ak.lower() or ak.lower() in k:
                return ak
    for ak, esler in es_anlamli.items():
        for es in esler:
            if es in anlamli:
                return ak
    return None

# Senaryo gösterimi
def senaryo_goster(row):
    st.subheader(f"📌 {row['Senaryo']}")
    st.markdown(f"**🔎 Açıklama:** {row['Açıklama']}")
    st.markdown(f"**🛠️ Çözüm:** {row['Çözüm']}")
    st.markdown(f"**👤 Sorumlu:** {row['Sorumlu']}")
    if pd.notna(row["Görsel"]) and row["Görsel"] != "":
        dosya_yolu = os.path.join("images", row["Görsel"])
        if os.path.exists(dosya_yolu):
            st.image(dosya_yolu, caption=row["Senaryo"], use_container_width=True)
        else:
            st.warning(f"⚠️ Hata ile ilgili görsel bulunamadı")

# Giriş yakalama
admin_giris = False
soru = st.text_input("📝 Sorunuzu yazın (örnek: sistem dondu, giriş yapamıyorum...)")

if soru.lower() == "cyadminacil":
    st.warning("🛡️ Yöneticiler için giriş ekranı")
    username = st.text_input("👤 Kullanıcı adı")
    password = st.text_input("🔑 Şifre", type="password")
    if username == "cmyvava" and password == "12345":
        admin_giris = True
    else:
        st.stop()

# ✅ Admin Panel
if admin_giris:
    st.success("✅ Giriş başarılı. Loglar aşağıda:")
    try:
        log_df = pd.read_excel("soru_loglari.xlsx")
        st.dataframe(log_df, use_container_width=True)

        st.download_button("📥 Excel olarak indir", data=log_df.to_excel(index=False),
                           file_name="soru_loglari.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        if st.button("🗑️ Logları Sıfırla"):
            os.remove("soru_loglari.xlsx")
            st.success("Log dosyası sıfırlandı. Sayfayı yenileyin.")
            st.stop()
    except:
        st.info("📁 Log dosyası henüz oluşmadı.")
    st.stop()

# 👤 Normal Kullanıcı Akışı
kullanici = st.text_input("👤 Kullanıcı adınız (isteğe bağlı):")

if soru and soru.lower() != "cyadminacil":
    anahtar = anahtar_kelime_bul(soru)
    if anahtar:
        senaryolar = df[df["Anahtar Kelime"].str.lower() == anahtar.lower()]
        if len(senaryolar) > 1:
            st.info(f"🧠 '{anahtar}' için {len(senaryolar)} senaryo bulundu:")
            secim = st.selectbox("Lütfen durumu seçin:", senaryolar["Senaryo"].tolist())
            secilen = senaryolar[senaryolar["Senaryo"] == secim].iloc[0]
            senaryo_goster(secilen)
        elif len(senaryolar) == 1:
            senaryo_goster(senaryolar.iloc[0])
        else:
            st.warning("⚠️ Eşleşen anahtar kelime bulundu ama senaryo bilgisi eksik.")
            logla(soru, kullanici, durum="Anahtar eşleşti ama senaryo yok")
    else:
        st.warning("🤖 Bu soruya dair kayıtlı bir bilgi bulunamadı.")
        logla(soru, kullanici)
