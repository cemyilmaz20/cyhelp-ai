import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import os

# Türkiye saatine göre zaman
def turkiye_saati():
    return (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

# Senaryo ekleme formu
def senaryo_ekle_formu():
    with st.expander("📝 Yeni Senaryo Ekle"):
        st.markdown("Yeni bir senaryo tanımı ekleyin. Bu bilgiler Excel'e yazılır.")
        anahtar = st.text_input("🔑 Anahtar Kelime")
        senaryo = st.text_input("📌 Senaryo Başlığı")
        aciklama = st.text_area("📖 Açıklama")
        cozum = st.text_area("🛠️ Çözüm")
        sorumlu = st.text_input("👤 Sorumlu Kişi")
        gorsel = st.text_input("🖼️ Görsel Dosya Adı (images klasörüne koymalısınız)")

        if st.button("✅ Senaryoyu Ekle"):
            yeni = pd.DataFrame([{
                "Anahtar Kelime": anahtar,
                "Senaryo": senaryo,
                "Açıklama": aciklama,
                "Çözüm": cozum,
                "Sorumlu": sorumlu,
                "Görsel": gorsel
            }])
            dosya = "veri.xlsx"
            if os.path.exists(dosya):
                mevcut = pd.read_excel(dosya)
                mevcut = pd.concat([mevcut, yeni], ignore_index=True)
            else:
                mevcut = yeni
            mevcut.to_excel(dosya, index=False)
            st.success("✅ Senaryo başarıyla eklendi.")

# Sık sorulan soruları tespit et
def sik_sorulan_kontrolu():
    st.subheader("📊 Sık Sorulan Sorular")
    try:
        logs = pd.read_excel("soru_loglari.xlsx")
        en_sik = logs["Soru"].value_counts().head(5)
        for soru, sayi in en_sik.items():
            st.markdown(f"- **{soru}** → {sayi} kez")
    except Exception as e:
        st.warning("⚠️ Soru logu bulunamadı.")

# Admin paneli: Senaryo düzenleme
def senaryo_duzenle_paneli():
    st.subheader("🛠️ Mevcut Senaryoları Düzenle")
    dosya = "veri.xlsx"
    if os.path.exists(dosya):
        df = pd.read_excel(dosya)
        senaryo_sec = st.selectbox("✏️ Düzenlenecek Senaryo", df["Senaryo"].tolist())
        secilen = df[df["Senaryo"] == senaryo_sec].iloc[0]

        yeni_aciklama = st.text_area("📖 Açıklama", secilen["Açıklama"])
        yeni_cozum = st.text_area("🛠️ Çözüm", secilen["Çözüm"])
        yeni_sorumlu = st.text_input("👤 Sorumlu", secilen["Sorumlu"])
        yeni_gorsel = st.text_input("🖼️ Görsel", secilen["Görsel"])

        if st.button("💾 Güncelle"):
            df.loc[df["Senaryo"] == senaryo_sec, ["Açıklama", "Çözüm", "Sorumlu", "Görsel"]] = \
                [yeni_aciklama, yeni_cozum, yeni_sorumlu, yeni_gorsel]
            df.to_excel(dosya, index=False)
            st.success("✅ Güncelleme tamamlandı.")
    else:
        st.warning("⚠️ veri.xlsx bulunamadı.")

# Toast tipi mini bilgilendirme
def toast_bildirim(mesaj, tipi="info"):
    if tipi == "success":
        st.success(mesaj)
    elif tipi == "warning":
        st.warning(mesaj)
    elif tipi == "error":
        st.error(mesaj)
    else:
        st.info(mesaj)
