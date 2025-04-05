import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="CYHELP", page_icon="🧠")
st.title("🔧 CYHELP | Yapay Zeka Destekli VAVA İş Akış Asistanı")

df = pd.read_excel("veri.xlsx")

soru = st.text_input("📝 Sorunuzu yazın (örnek: sistem dondu, giriş yapamıyorum...):")

# Eşleşen anahtar kelimelerden senaryo çıkar
def senaryo_bul(kelime):
    senaryolar = df[df["Anahtar Kelime"].str.lower() == kelime.lower()]
    return senaryolar

# Cümleden kelime yakala
def yakala(cumle):
    cumle = cumle.lower()
    for kelime in df["Anahtar Kelime"].unique():
        if kelime.lower() in cumle:
            return kelime
    return None

# Seçilen senaryoyu göster
def senaryo_goster(row):
    st.subheader(f"📌 {row['Senaryo']}")
    st.markdown(f"**🔎 Açıklama:** {row['Açıklama']}")
    st.markdown(f"**🛠️ Çözüm:** {row['Çözüm']}")
    st.markdown(f"**👤 Sorumlu:** {row['Sorumlu']}")
    if pd.notna(row["Görsel"]) and row["Görsel"] != "":
        st.image(f"images/{row['Görsel']}", caption=row["Senaryo"], use_column_width=True)

if soru:
    bulunan = yakala(soru)
    if bulunan:
        senaryolar = senaryo_bul(bulunan)
        st.info(f"🧠 '{bulunan}' ile ilgili {len(senaryolar)} çözüm bulundu:")
        secim = st.selectbox("Hangi durumu yaşıyorsunuz?", senaryolar["Senaryo"].tolist())
        secilen = senaryolar[senaryolar["Senaryo"] == secim].iloc[0]
        senaryo_goster(secilen)
    else:
        st.warning("🤖 Bu soruya dair eşleşen bir kayıt bulunamadı. Cem YILMAZ'a sorun :) ")
