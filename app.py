import streamlit as st
import pandas as pd
import datetime
import os
from io import BytesIO

# Sayfa başlığı ve ayarları
st.set_page_config(page_title="CYHELP | VAVA İş Akış Asistanı", page_icon="🧠")

st.markdown("""
<h1 style='display: flex; align-items: center; gap: 10px;'>
  🧠 CYHELP | Yapay Zeka Destekli <br> VAVA İş Akış Asistanı
</h1>
""", unsafe_allow_html=True)

# Gerekli dosyalar
df = pd.read_excel("veri.xlsx")
LOG_FILE = "soru_loglari.xlsx"

# Admin bilgiler
GIZLI_KELIME = "cyadminacil"
ADMIN_KULLANICI = "cmyvava"
ADMIN_SIFRE = "12345"

# Oturum başlatma
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# Log kaydetme fonksiyonu
def log_kaydet(soru, durum, kullanici):
    log = {
        "Tarih": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Soru": soru,
        "Durum": durum,
        "Kullanıcı": kullanici if kullanici else "-"
    }
    try:
        if os.path.exists(LOG_FILE):
            df_log = pd.read_excel(LOG_FILE)
            df_log = pd.concat([df_log, pd.DataFrame([log])], ignore_index=True)
        else:
            df_log = pd.DataFrame([log])
        df_log.to_excel(LOG_FILE, index=False)
    except Exception as e:
        st.warning(f"⚠️ Log kaydedilemedi: {e}")
# Senaryo gösterimi
def senaryo_goster(row):
    st.subheader(f"📌 {row['Senaryo']}")
    st.markdown(f"**🔎 Açıklama:** {row['Açıklama']}")
    st.markdown(f"**🛠️ Çözüm:** {row['Çözüm']}")
    st.markdown(f"**👤 Sorumlu:** {row['Sorumlu']}")
    if pd.notna(row["Görsel"]) and row["Görsel"] != "":
        st.image(f"images/{row['Görsel']}", caption=row["Senaryo"], use_column_width=True)
    else:
        st.warning("⚠️ Hata ile ilgili görsel bulunamadı")

# Anahtar kelime yakalama
def yakala(cumle):
    cumle = cumle.lower()
    for kelime in df["Anahtar Kelime"].dropna().unique():
        if str(kelime).lower() in cumle:
            return kelime
    return None

# Admin paneli
def admin_paneli():
    st.success("✅ Giriş başarılı. Loglar aşağıda:")

    if os.path.exists(LOG_FILE):
        logs = pd.read_excel(LOG_FILE)
        st.dataframe(logs, use_container_width=True)

        excel_buffer = BytesIO()
        logs.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        st.download_button("📥 Excel olarak indir", data=excel_buffer, file_name="loglar.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        if st.button("🗑️ Logları sıfırla"):
            os.remove(LOG_FILE)
            st.warning("🧹 Log dosyası silindi.")
    else:
        st.info("📂 Log dosyası henüz oluşmadı.")

    if st.button("🚪 Oturumu Kapat"):
        st.session_state.admin_mode = False
        st.rerun()

# Giriş alanları
soru = st.text_input("📝 Sorunuzu yazın (örnek: sistem dondu, giriş yapamıyorum...)")
kullanici = st.text_input("👤 Kullanıcı adınız (isteğe bağlı):")

# Admin girişi
if st.session_state.admin_mode:
    admin_paneli()
    st.stop()

if soru.strip().lower() == GIZLI_KELIME:
    st.warning("🔒 Yetkili girişi yapılıyor...")
    user = st.text_input("👤 Kullanıcı Adı")
    pw = st.text_input("🔑 Şifre", type="password")
    if user == ADMIN_KULLANICI and pw == ADMIN_SIFRE:
        st.session_state.admin_mode = True
        st.rerun()
    else:
        st.warning("❌ Hatalı kullanıcı adı veya şifre")
    st.stop()

# Normal kullanıcı işlemleri
elif soru:
    bulunan = yakala(soru)
    if bulunan:
        senaryolar = df[df["Anahtar Kelime"].str.lower() == bulunan.lower()]
        if senaryolar.empty:
            st.warning("⚠️ Eşleşen anahtar kelime bulundu ama senaryo bilgisi eksik.")
            log_kaydet(soru, "Anahtar eşleşti ama senaryo yok", kullanici)
        elif len(senaryolar) == 1:
            secilen = senaryolar.iloc[0]
            senaryo_goster(secilen)
            log_kaydet(soru, "Senaryo gösterildi", kullanici)
        else:
            st.info(f"🧠 '{bulunan}' ile ilgili birden fazla senaryo bulundu:")
            secim = st.selectbox("Lütfen neyi kastettiğinizi seçin:", senaryolar["Senaryo"].tolist())
            secilen = senaryolar[senaryolar["Senaryo"] == secim].iloc[0]
            senaryo_goster(secilen)
            log_kaydet(soru, "Senaryo seçildi", kullanici)
    else:
        st.warning("🤖 Bu soruya dair kayıtlı bir bilgi bulunamadı.")
        log_kaydet(soru, "Eşleşme bulunamadı", kullanici)
