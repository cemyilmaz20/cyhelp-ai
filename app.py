import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re

st.set_page_config(page_title="CYHELP", page_icon="🧠")
st.title("🔧 CYHELP | Yapay Zeka Destekli VAVA İş Akış Asistanı")

# Veri dosyasını yükle
df = pd.read_excel("veri.xlsx")

# Soruyu al
soru = st.text_input("📝 Sorunuzu yazın (örnek: sistem dondu, giriş yapamıyorum...)")

# Basit Türkçe stopword listesi
stop_words = ["ben", "bir", "bu", "şu", "ve", "ile", "de", "da", "ama", "çok", "neden", "nasıl"]

# Görselli senaryo gösterici
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

# Anahtar kelimeyi bul (GPT’siz doğal dil işleme)
def anahtar_kelime_bul(soru):
    kelimeler = re.findall(r'\b\w+\b', soru.lower())
    anlamli = [kelime for kelime in kelimeler if kelime not in stop_words]
    for k in anlamli:
        for ak in df["Anahtar Kelime"].unique():
            if k in ak.lower() or ak.lower() in k:
                return ak
    return None

# Soru logla (eşleşme bulunamazsa)
def logla(soru):
    log_yolu = "soru_loglari.xlsx"
    yeni_kayit = pd.DataFrame([{
        "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Soru": soru,
        "Durum": "Eşleşme bulunamadı"
    }])
    try:
        mevcut_log = pd.read_excel(log_yolu)
        log_df = pd.concat([mevcut_log, yeni_kayit], ignore_index=True)
    except:
        log_df = yeni_kayit
    log_df.to_excel(log_yolu, index=False)

# Ana sistem
if soru:
    anahtar = anahtar_kelime_bul(soru)
    if anahtar:
        senaryolar = df[df["Anahtar Kelime"].str.lower() == anahtar.lower()]
        if len(senaryolar) > 1:
            st.info(f"🧠 '{anahtar}' için {len(senaryolar)} senaryo bulundu:")
            secim = st.selectbox("Lütfen durumu seçin:", senaryolar["Senaryo"].tolist())
            secilen = senaryolar[senaryolar["Senaryo"] == secim].iloc[0]
            senaryo_goster(secilen)
        else:
            senaryo_goster(senaryolar.iloc[0])
    else:
        st.warning("🤖 Bu soruya dair kayıtlı bir bilgi bulunamadı.")
        logla(soru)
