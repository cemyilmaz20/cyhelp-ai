
import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="CYHELP | Yapay Zeka Destekli VAVA İş Akış Asistanı", page_icon="🧠")

# Başlık
st.markdown("<h1 style='text-align: center;'>🧠 CYHELP | Yapay Zeka Destekli<br>VAVA İş Akış Asistanı</h1>", unsafe_allow_html=True)

# Gizli admin tetikleyici
arama = st.text_input("📝 Sorunuzu yazın (örnek: sistem dondu, giriş yapamıyorum...)", key="arama_input")

# Admin ekranı tetiklenirse
if arama == "cyadminacil":
    with st.expander("🔐 Yetkili girişi yapılıyor...", expanded=True):
        kullanici = st.text_input("👤 Kullanıcı Adı", key="admin_user")
        sifre = st.text_input("🔑 Şifre", type="password", key="admin_pass")
        if kullanici == "cmyvava" and sifre == "12345":
            st.success("✅ Giriş başarılı. Loglar aşağıda:")
            try:
                df = pd.read_excel("soru_loglari.xlsx")
                st.dataframe(df)

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False)
                st.download_button("📥 Excel olarak indir", data=buffer.getvalue(), file_name="loglar.xlsx")

                if st.button("🗑️ Logları sıfırla"):
                    df = pd.DataFrame(columns=["Tarih", "Soru", "Durum", "Kullanıcı"])
                    df.to_excel("soru_loglari.xlsx", index=False)
                    st.success("🧹 Log dosyası sıfırlandı. Sayfayı yenileyin.")

                if st.button("🚪 Oturumu Kapat"):
                    st.session_state.clear()
                    st.experimental_rerun()

            except FileNotFoundError:
                st.info("📁 Log dosyası henüz oluşmadı.")
        elif kullanici or sifre:
            st.error("❌ Hatalı kullanıcı adı veya şifre")

else:
    # Kullanıcı arayüzü
    kullanici_adi = st.text_input("👤 Kullanıcı adınız (isteğe bağlı):", key="normal_user")
    df = pd.read_excel("veri.xlsx")

    def yakala(cumle):
        cumle = cumle.lower()
        for kelime in df["Anahtar Kelime"].unique():
            if kelime.lower() in cumle:
                return kelime
        return None

    def senaryo_goster(row):
        st.subheader(f"📌 {row['Senaryo']}")
        st.markdown(f"**🔎 Açıklama:** {row['Açıklama']}")
        st.markdown(f"**🛠️ Çözüm:** {row['Çözüm']}")
        st.markdown(f"**👤 Sorumlu:** {row['Sorumlu']}")
        if pd.notna(row["Görsel"]) and row["Görsel"] != "":
            st.image(f"images/{row['Görsel']}", caption=row["Senaryo"], use_column_width=True)
        else:
            st.warning(f"⚠️ Hata ile ilgili görsel bulunamadı")

    if arama:
        bulunan = yakala(arama)
        if bulunan:
            senaryolar = df[df["Anahtar Kelime"].str.lower() == bulunan.lower()]
            if not senaryolar.empty:
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

        # Log yaz
        yeni_kayit = pd.DataFrame([{
            "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Soru": arama,
            "Durum": durum,
            "Kullanıcı": kullanici_adi if kullanici_adi else "-"
        }])
        try:
            eski_log = pd.read_excel("soru_loglari.xlsx")
            log_df = pd.concat([eski_log, yeni_kayit], ignore_index=True)
        except:
            log_df = yeni_kayit
        log_df.to_excel("soru_loglari.xlsx", index=False)
