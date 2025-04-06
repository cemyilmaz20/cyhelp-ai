import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="CYHELP | VAVA İş Akış Asistanı", page_icon="🧠")

# Logo ve başlık
st.markdown("<h1 style='text-align: center;'>🧠 CYHELP | Yapay Zeka Destekli<br>VAVA İş Akış Asistanı</h1>", unsafe_allow_html=True)

# Excel yükle
df = pd.read_excel("veri.xlsx")

# Gizli admin tetikleyici
soru_input = st.text_input("📝 Sorunuzu yazın (örnek: sistem dondu, giriş yapamıyorum...)", key="soru")

# Global log listesi
if "logs" not in st.session_state:
    st.session_state.logs = []

# Admin girişi tetikleme
if soru_input.strip().lower() == "cyadminacil":
    with st.expander("🔐 Yetkili girişi yapılıyor...", expanded=True):
        username = st.text_input("👤 Kullanıcı Adı", key="admin_user")
        password = st.text_input("🔑 Şifre", type="password", key="admin_pass")

        if username == "cmyvava" and password == "12345":
            st.success("✅ Giriş başarılı. Loglar aşağıda:")
            logs = pd.DataFrame(st.session_state.logs, columns=["Tarih", "Soru", "Durum", "Kullanıcı"])
            st.dataframe(logs, use_container_width=True)

            if len(logs) > 0:
                st.download_button("📥 Excel olarak indir", data=logs.to_csv(index=False).encode("utf-8"), file_name="soru_loglari.csv", mime="text/csv")
                if st.button("🗑️ Logları sıfırla"):
                    st.session_state.logs = []
                    st.rerun()

            if st.button("🚪 Oturumu Kapat"):
               st.session_state.pop("admin_user", None)
               st.session_state.pop("admin_pass", None)
               st.session_state["soru"] = ""  # ← cyadminacil ifadesini temizle
               st.rerun()

        elif username or password:
            st.error("❌ Hatalı kullanıcı adı veya şifre")

# Normal kullanıcı arayüzü
else:
    kullanici_adi = st.text_input("👤 Kullanıcı adınız (isteğe bağlı):", key="kullanici")

    # Anahtar kelime eşleştir
    def yakala(cumle):
        cumle = cumle.lower()
        for kelime in df["Anahtar Kelime"].unique():
            if str(kelime).lower() in cumle:
                return kelime
        return None

    def senaryo_bul(kelime):
        return df[df["Anahtar Kelime"].str.lower() == kelime.lower()]

    def senaryo_goster(row):
        st.subheader(f"📌 {row['Senaryo']}")
        st.markdown(f"**🔎 Açıklama:** {row['Açıklama']}")
        st.markdown(f"**🛠️ Çözüm:** {row['Çözüm']}")
        st.markdown(f"**👤 Sorumlu:** {row['Sorumlu']}")
        if pd.notna(row["Görsel"]) and row["Görsel"] != "":
            st.image(f"images/{row['Görsel']}", caption=row["Senaryo"], use_column_width=True)
        else:
            st.warning(f"⚠️ Hata ile ilgili görsel bulunamadı")

    if soru_input:
        bulunan = yakala(soru_input)
        if bulunan:
            senaryolar = senaryo_bul(bulunan)
            if not senaryolar.empty:
                st.info(f"🧠 '{bulunan}' ile ilgili {len(senaryolar)} çözüm bulundu:")
                secim = st.selectbox("Lütfen neyi kastettiğinizi seçin:", senaryolar["Senaryo"].tolist())
                secilen = senaryolar[senaryolar["Senaryo"] == secim].iloc[0]
                senaryo_goster(secilen)
                durum = "Eşleşme bulundu"
            else:
                st.warning("⚠️ Eşleşen anahtar kelime bulundu ama senaryo bilgisi eksik.")
                durum = "Anahtar eşleşti ama senaryo yok"
        else:
            st.warning("🤖 Bu soruya dair kayıtlı bir bilgi bulunamadı.")
            durum = "Eşleşme bulunamadı"

        # Log ekle
        yeni_kayit = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), soru_input, durum, kullanici_adi if kullanici_adi else "-"]
        st.session_state.logs.append(yeni_kayit)
