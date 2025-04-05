import streamlit as st
import pandas as pd

st.set_page_config(page_title="CYHELP", page_icon="🧠")
st.title("🔧 CYHELP | Yapay Zeka Destekli İş Akış Asistanı")

df = pd.read_excel("veri.xlsx")

soru = st.text_input("Sisteme dair bir sorun ya da soru yazın:")

def cevapla(soru):
    soru = soru.lower()
    for i, row in df.iterrows():
        if row["Anahtar Kelime"].lower() in soru:
            return f"**Açıklama:** {row['Açıklama']}

**Çözüm:** {row['Çözüm']}

**Sorumlu:** {row['Sorumlu']}"
    return "🤖 Bu soruya dair kayıtlı bir bilgi bulunamadı."

if soru:
    st.markdown(cevapla(soru))
