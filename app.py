import streamlit as st
import pandas as pd

st.set_page_config(page_title="CYHELP", page_icon="🧠")
st.title("🔧 CYHELP | Yapay Zeka Destekli VAVA İş Akış Asistanı")

# Excel'den verileri çekiyoruz
df = pd.read_excel("veri.xlsx")

# Soru giriş kutusu
soru = st.text_input("📝 Sorunuzu yazın (örnek: sistem dondu, giriş yapamıyorum...)")

# Anahtar kelime eşleştiricisi
def yakala(cumle):
    cumle = cumle.lower()
    for kelime in df["Anahtar Kelime"].unique():
        if kelime.lower() in cumle:
            return kelime
    return None

# Senaryoya ait bilgileri göster
def senaryo_goster(row):
    st.subheader(f"📌 {row['Senaryo']}")
    st.markdown(f"**🔎 Açıklama:** {row['Açıklama']}")
    st.markdown(f"**🛠️ Çözüm:** {row['Çözüm']}")
    st.markdown(f"**👤 Sorumlu:** {row['Sorumlu']}")
    if pd.notna(row["Görsel"]) and row["Görsel"] != "":
        st.image(f"images/{row['Görsel']}", caption=row["Senaryo"], use_column_width=True)

# Kullanıcı soru girerse işleme başla
if soru:
    bulunan = yakala(soru)

    if bulunan:
        # Aynı kelimeye karşılık gelen tüm senaryoları getir
        senaryolar = df[df["Anahtar Kelime"].str.lower() == bulunan.lower()]

        if len(senaryolar) > 1:
            st.info(f"🧠 '{bulunan}' kelimesi için {len(senaryolar)} farklı senaryo bulundu:")
            secim = st.selectbox("Lütfen neyi kastettiğinizi seçin:", senaryolar["Senaryo"].tolist())
            secilen = senaryolar[senaryolar["Senaryo"] == secim].iloc[0]
            senaryo_goster(secilen)
        else:
            senaryo_goster(senaryolar.iloc[0])
    else:
        st.warning("🤖 Bu kelimeyle eşleşen bir çözüm bulunamadı. Cem YILMAZ’a sor 😎")
