import streamlit as st
import pandas as pd

st.set_page_config(page_title="CYHELP", page_icon="🧠")
st.title("🔧 CYHELP | Yapay Zeka Destekli VAVA İş Akış Asistanı")

df = pd.read_excel("veri.xlsx")

soru = st.text_input("SalesForce'a dair bir sorun ya da soru yazın:")

def cevapla(soru):
    soru = soru.lower()
    for i, row in df.iterrows():
        if row["Anahtar Kelime"].lower() in soru:
            return f"""**Açıklama:** {row['Açıklama']}\n\n**Çözüm:** {row['Çözüm']}\n\n**Sorumlu:** {row['Sorumlu']}"""
    return "🤖 Bu soruya dair kayıtlı bir bilgi bulunamadı. Cem YILMAZ ile iletişime geçebilirsin :)"

if soru:
    st.markdown(cevapla(soru))
