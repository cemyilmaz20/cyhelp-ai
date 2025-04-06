
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Başlık ve yapılandırma
st.set_page_config(page_title="CYHELP | Yapay Zeka Destekli VAVA İş Akış Asistanı", page_icon="🧠")
st.markdown("<h1 style='text-align: center;'>🧠 CYHELP | Yapay Zeka Destekli<br> VAVA İş Akış Asistanı</h1>", unsafe_allow_html=True)

# Excel ve log dosya adları
DATA_FILE = "veri.xlsx"
LOG_FILE = "soru_loglari.xlsx"

# Admin bilgileri
ADMIN_TRIGGER = "cyadminacil"
ADMIN_USERNAME = "cmyvava"
ADMIN_PASSWORD = "12345"

# Excel varsa yükle
@st.cache_data
def load_data():
    return pd.read_excel(DATA_FILE)

# Log yükle
@st.cache_data
def load_logs():
    if os.path.exists(LOG_FILE):
        return pd.read_excel(LOG_FILE)
    else:
        return pd.DataFrame(columns=["Tarih", "Soru", "Durum", "Kullanıcı"])

# Log kaydet
def save_log(tarih, soru, durum, kullanici=None):
    logs = load_logs()
    new_row = pd.DataFrame([{
        "Tarih": tarih,
        "Soru": soru,
        "Durum": durum,
        "Kullanıcı": kullanici if kullanici else "-"
    }])
    logs = pd.concat([logs, new_row], ignore_index=True)
    logs.to_excel(LOG_FILE, index=False)

# Logları sıfırla
def reset_logs():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

# Anahtar kelime eşleştir
def yakala(cumle, df):
    cumle = cumle.lower()
    for kelime in df["Anahtar Kelime"].dropna().unique():
        if str(kelime).lower() in cumle:
            return kelime
    return None

# Senaryoyu göster
def senaryo_goster(row):
    st.subheader(f"📌 {row['Senaryo']}")
    st.markdown(f"**🔎 Açıklama:** {row['Açıklama']}")
    st.markdown(f"**🛠️ Çözüm:** {row['Çözüm']}")
    st.markdown(f"**👤 Sorumlu:** {row['Sorumlu']}")
    if pd.notna(row.get("Görsel")) and row["Görsel"] != "":
        try:
            st.image(f"images/{row['Görsel']}", caption=row["Senaryo"])
        except:
            st.warning("⚠️ Hata ile ilgili görsel bulunamadı")

# Uygulama başlangıcı
veri = load_data()

# Admin tetikleyici kontrol
soru = st.text_input("📝 Sorunuzu yazın (örnek: sistem dondu, giriş yapamıyorum...):", key="soru")
kullanici_adi = st.text_input("👤 Kullanıcı adınız (isteğe bağlı):", key="kullanici_adi")

if ADMIN_TRIGGER in soru:
    st.session_state["admin_mode"] = True

# Admin paneli
if st.session_state.get("admin_mode"):
    with st.expander("🔐 Yetkili girişi yapılıyor..."):
        admin_user = st.text_input("👤 Kullanıcı Adı", key="admin_user_input")
        admin_pass = st.text_input("🔑 Şifre", type="password", key="admin_pass_input")

        if admin_user == ADMIN_USERNAME and admin_pass == ADMIN_PASSWORD:
            st.success("✅ Giriş başarılı. Loglar aşağıda:")
            logs = load_logs()

            st.markdown("### 📊 Soru Logları")
            st.dataframe(logs)

            if not logs.empty:
                st.download_button("📥 Excel olarak indir", data=logs.to_csv(index=False).encode("utf-8"), file_name="loglar.csv", mime="text/csv")
                if st.button("🗑️ Logları sıfırla"):
                    reset_logs()
                    st.success("Loglar silindi.")
                    st.rerun()
            else:
                st.info("📂 Log dosyası henüz oluşmadı.")

            if st.button("🪑 Oturumu Kapat"):
                for key in ["admin_mode", "admin_user_input", "admin_pass_input"]:
                    st.session_state.pop(key, None)
                st.rerun()
        elif admin_user and admin_pass:
            st.error("❌ Hatalı kullanıcı adı veya şifre")

elif soru:
    bulunan = yakala(soru, veri)
    if bulunan:
        senaryolar = veri[veri["Anahtar Kelime"].str.lower() == bulunan.lower()]
        if not senaryolar.empty:
            st.info(f"🧠 '{bulunan}' ile ilgili {len(senaryolar)} çözüm bulundu:")
            secim = st.selectbox("Lütfen neyi kastettiğinizi seçin:", senaryolar["Senaryo"].tolist())
            secilen = senaryolar[senaryolar["Senaryo"] == secim].iloc[0]
            senaryo_goster(secilen)
            save_log(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), soru, "Eşleşme bulundu", kullanici_adi)
        else:
            st.warning("⚠️ Eşleşen anahtar kelime bulundu ama senaryo bilgisi eksik.")
            save_log(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), soru, "Anahtar eşleşti ama senaryo yok", kullanici_adi)
    else:
        st.warning("🤖 Bu soruya dair kayıtlı bir bilgi bulunamadı.")
        save_log(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), soru, "Eşleşme bulunamadı", kullanici_adi)
