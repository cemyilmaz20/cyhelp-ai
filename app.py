import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime

st.set_page_config(page_title="CYHELP", page_icon="🧠")
st.title("🔧 CYHELP | Yapay Zeka Destekli VAVA İş Akış Asistanı")

df = pd.read_excel("veri.xlsx")

stop_words = ["ben", "bir", "bu", "şu", "ve", "ile", "de", "da", "ama", "çok", "neden", "nasıl", "şey", "gibi", "ki"]

es_anlamli = {
    "dondu": ["kitlendi", "takıldı", "çöktü", "donuyor", "kasma"],
    "giriş": ["login", "şifre", "oturum", "giremiyorum"],
    "ruhsat": ["belge", "noter evrağı", "vesika"],
    "çalışmıyor": ["açılmıyor", "başlamıyor", "görünmüyor"]
}

kullanici = st.text_input("👤 Kullanıcı adınız (isteğe bağlı):")
soru = st.text_input("📝 Sorunuzu yazın (örnek: sistem dondu, giriş yapamıyorum...)")

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

def logla(soru, kullanici):
    log_yolu = "soru_loglari.xlsx"
    yeni_kayit = pd.DataFrame([{
        "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Kullanıcı": kullanici if kullanici else "-",
        "Soru": soru,
        "Durum": "Eşleşme bulunamadı"
    }])
    try:
        mevcut = pd.read_excel(log_yolu)
        log_df = pd.concat([mevcut, yeni_kayit], ignore_index=True)
    except:
        log_df = yeni_kayit
    log_df.to_excel(log_yolu, index=False)

# Ana akış
if soru:
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
            logla(soru, kullanici)
    else:
        st.warning("🤖 Bu soruya dair kayıtlı bir bilgi bulunamadı.")
        logla(soru, kullanici)
