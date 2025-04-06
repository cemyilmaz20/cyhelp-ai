import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import os

# Türkiye saatine göre zaman
def turkiye_saati():
    return (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

# Bildirim (toast gibi)
def toast_bildirim(mesaj, tipi="info"):
    if tipi == "success":
        st.success(mesaj)
    elif tipi == "warning":
        st.warning(mesaj)
    elif tipi == "error":
        st.error(mesaj)
    else:
        st.info(mesaj)

# Yeni senaryo ekleme formu (expander KALDIRILDI!)
def senaryo_ekle_formu():
    st.markdown("### ➕ Yeni Senaryo Ekle")
    with st.form("senaryo_ekle_form", clear_on_submit=True):
        anahtar = st.text_input("🔑 Anahtar Kelime")
        senaryo = st.text_input("📌 Senaryo Başlığı")
        aciklama = st.text_area("📖 Açıklama")
        cozum = st.text_area("🛠️ Çözüm")
        sorumlu = st.text_input("👤 Sorumlu")
        gorsel = st.text_input("🖼️ Görsel Dosya Adı (images klasörüne yüklenmeli)")

        ekle = st.form_submit_button("✅ Ekle")
        if ekle and anahtar and senaryo:
            dosya = "veri.xlsx"
            # Eğer dosya var ise oku, yoksa yeni oluştur
            if os.path.exists(dosya):
                df = pd.read_excel(dosya)
            else:
                df = pd.DataFrame(columns=["Anahtar Kelime", "Senaryo", "Açıklama", "Çözüm", "Sorumlu", "Görsel"])

            # Yeni senaryoyu ekle
            yeni = pd.DataFrame([{
                "Anahtar Kelime": anahtar,
                "Senaryo": senaryo,
                "Açıklama": aciklama,
                "Çözüm": cozum,
                "Sorumlu": sorumlu,
                "Görsel": gorsel
            }])
            df = pd.concat([df, yeni], ignore_index=True)  # Yeni senaryoyu ekle
            df.to_excel(dosya, index=False)  # Veriyi kaydet

            st.success("✅ Yeni senaryo başarıyla eklendi.")
            st.rerun()  # Sayfayı yenileyerek yeni veriyi doğru şekilde yükleyelim.

# Mevcut senaryoyu düzenleme paneli
def senaryo_duzenle_paneli():
    st.markdown("### ✏️ Mevcut Senaryoları Düzenle")
    dosya = "veri.xlsx"
    if not os.path.exists(dosya):
        st.warning("⚠️ veri.xlsx bulunamadı.")
        return
    df = pd.read_excel(dosya)
    if df.empty:
        st.info("Veri dosyası boş.")
        return
    secim = st.selectbox("Düzenlenecek Senaryo", df["Senaryo"].tolist())
    secilen = df[df["Senaryo"] == secim].iloc[0]

    yeni_aciklama = st.text_area("📖 Açıklama", value=secilen["Açıklama"])
    yeni_cozum = st.text_area("🛠️ Çözüm", value=secilen["Çözüm"])
    yeni_sorumlu = st.text_input("👤 Sorumlu", value=secilen["Sorumlu"])
    yeni_gorsel = st.text_input("🖼️ Görsel", value=secilen["Görsel"])

    if st.button("💾 Güncelle"):
        # Anahtar kelimeyi de güncelliyoruz
        df.loc[df["Senaryo"] == secim, ["Anahtar Kelime", "Açıklama", "Çözüm", "Sorumlu", "Görsel"]] = \
            [secilen["Anahtar Kelime"], yeni_aciklama, yeni_cozum, yeni_sorumlu, yeni_gorsel]
        df.to_excel(dosya, index=False)
        st.success("✅ Güncelleme tamamlandı.")

# Sık gelen sorular listesi (öğrenen yapı)
def sik_sorulan_kontrolu():
    st.markdown("### 🔁 Sık Sorulan Sorular")
    log_path = "soru_loglari.xlsx"
    if not os.path.exists(log_path):
        st.info("Soru logu bulunamadı.")
        return
    df = pd.read_excel(log_path)
    populer = df["Soru"].value_counts().head(5)
    for soru, adet in populer.items():
        st.markdown(f"- **{soru}** → {adet} kez")
