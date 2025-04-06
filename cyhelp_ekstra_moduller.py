import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import os

# Türkiye saatine göre zaman
def turkiye_saati():
    return (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

# Başarı mesajının kaybolmaması için
def success_message_display():
    if "success_message" in st.session_state:
        st.success(st.session_state["success_message"])
        del st.session_state["success_message"]  # Mesaj bir kez gösterildikten sonra sil

# Yeni senaryo ekleme formu
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

            # Yeni veriyi mevcut veriye ekle
            df = pd.concat([df, yeni], ignore_index=True)

            # Dosyayı kaydet
            try:
                df.to_excel(dosya, index=False)
                print("Veri başarıyla kaydedildi.")
                st.session_state["success_message"] = "✅ Yeni senaryo başarıyla eklendi."  # Mesajı sakla
                st.rerun()  # Sayfayı yenileyerek yeni veriyi doğru şekilde yükleyelim
            except Exception as e:
                print(f"Error while saving to Excel: {str(e)}")
                st.error(f"❌ Senaryo eklenirken hata oluştu: {str(e)}")

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

    yeni_anahtar = st.text_input("🔑 Anahtar Kelime", value=secilen["Anahtar Kelime"])
    yeni_aciklama = st.text_area("📖 Açıklama", value=secilen["Açıklama"])
    yeni_cozum = st.text_area("🛠️ Çözüm", value=secilen["Çözüm"])
    yeni_sorumlu = st.text_input("👤 Sorumlu", value=secilen["Sorumlu"])
    yeni_gorsel = st.text_input("🖼️ Görsel", value=secilen["Görsel"])

    if st.button("💾 Güncelle"):
        print(f"Updating scenario: {secilen['Senaryo']} with new values.")  # Debugging
        print(f"New Key: {yeni_anahtar}, New Description: {yeni_aciklama}")

        try:
            df.loc[df["Senaryo"] == secim, ["Anahtar Kelime", "Açıklama", "Çözüm", "Sorumlu", "Görsel"]] = \
                [yeni_anahtar, yeni_aciklama, yeni_cozum, yeni_sorumlu, yeni_gorsel]
            df.to_excel(dosya, index=False)
            st.session_state["success_message"] = "✅ Güncelleme tamamlandı."  # Mesajı sakla
            st.rerun()  # Sayfayı yenileyerek yeni veriyi doğru şekilde yükleyelim
        except Exception as e:
            print(f"Error while updating Excel: {str(e)}")  # Debugging
            st.error(f"❌ Güncelleme sırasında hata oluştu: {str(e)}")

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

# Başarı mesajını ekranda tutma
success_message_display()

