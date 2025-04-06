from datetime import datetime
import pandas as pd
import streamlit as st
import os

# Sayfa ayarları
st.set_page_config(page_title="CYHELP | VAVA İş Akış Asistanı", page_icon="🧠")
st.markdown("<h1 style='text-align: center;'>🧠 CYHELP | Yapay Zeka Destekli<br>VAVA İş Akış Asistanı</h1>", unsafe_allow_html=True)

# Dosya yolları
EXCEL_PATH = "veri.xlsx"
LOG_PATH = "soru_loglari.xlsx"

# Log yükle veya oluştur
if os.path.exists(LOG_PATH):
    logs = pd.read_excel(LOG_PATH)
else:
    logs = pd.DataFrame(columns=["Tarih", "Soru", "Durum", "Kullanıcı"])

# Ana veri
df = pd.read_excel(EXCEL_PATH)

# Session başlangıcı
if "admin_user" not in st.session_state:
    st.session_state["admin_user"] = None
if "soru" not in st.session_state:
    st.session_state["soru"] = ""

# Giriş alanı
soru = st.text_input("📝 Sorunuzu yazın (örnek: sistem dondu, giriş yapamıyorum...)", value=st.session_state["soru"])
st.session_state["soru"] = soru
kullanici = st.text_input("👤 Kullanıcı adınız (isteğe bağlı):", key="kullanici_adi")

# Gizli admin giriş ekranı
if soru.lower() == "cyadminacil":
    with st.expander("🔐 Yetkili girişi yapılıyor..."):
        admin_user = st.text_input("👤 Kullanıcı Adı", key="admin_user_input")
        admin_pass = st.text_input("🔑 Şifre", type="password")
        if st.button("Giriş"):
            if admin_user == "cmyvava" and admin_pass == "12345":
                st.session_state["admin_user"] = admin_user
                st.success("✅ Giriş başarılı. Loglar aşağıda:")
            else:
                st.error("❌ Hatalı kullanıcı adı veya şifre")

# Admin panel
if st.session_state["admin_user"]:
    st.success("✅ Giriş başarılı. Loglar aşağıda:")
    st.dataframe(logs)

    if not logs.empty:
        st.download_button("📥 Excel olarak indir", data=logs.to_excel(index=False), file_name="loglar.xlsx")

        if st.button("🗑️ Logları sıfırla"):
            logs = pd.DataFrame(columns=["Tarih", "Soru", "Durum", "Kullanıcı"])
            if os.path.exists(LOG_PATH):
                os.remove(LOG_PATH)
            st.rerun()

    if st.button("🚪 Oturumu Kapat"):
        st.session_state["admin_user"] = None
        st.session_state["soru"] = ""
        st.rerun()

    if logs.empty:
        st.info("📂 Log dosyası henüz oluşmadı.")

# Anahtar kelime yakalama
def yakala(cumle):
    cumle = cumle.lower()
    for kelime in df["Anahtar Kelime"].dropna().unique():
        if kelime.lower() in cumle:
            return kelime
    return None

# Senaryo gösterme
def senaryo_goster(row):
    st.subheader(f"📌 {row['Senaryo']}")
    st.markdown(f"**🔎 Açıklama:** {row['Açıklama']}")
    st.markdown(f"**🛠️ Çözüm:** {row['Çözüm']}")
    st.markdown(f"**👤 Sorumlu:** {row['Sorumlu']}")
    if pd.notna(row["Görsel"]) and row["Görsel"] != "":
        st.image(f"images/{row['Görsel']}", caption=row["Senaryo"], use_column_width=True)
    else:
        st.warning(f"⚠️ Hata ile ilgili görsel bulunamadı")

# Soru işleme
if soru and soru.lower() != "cyadminacil" and not st.session_state["admin_user"]:
    bulunan = yakala(soru)
    if bulunan:
        senaryolar = df[df["Anahtar Kelime"].str.lower() == bulunan]
        if not senaryolar.empty:
            st.info(f"🧠 '{bulunan}' kelimesiyle ilgili {len(senaryolar)} senaryo bulundu:")
            secim = st.selectbox("Lütfen neyi kastettiğinizi seçin:", senaryolar["Senaryo"].tolist())
            secilen = senaryolar[senaryolar["Senaryo"] == secim].iloc[0]
            senaryo_goster(secilen)
            yeni_log = {"Tarih": datetime.now(), "Soru": soru, "Durum": "Eşleşme bulundu", "Kullanıcı": kullanici if kullanici else "-"}
        else:
            st.warning("⚠️ Eşleşen anahtar kelime bulundu ama senaryo bilgisi eksik.")
            yeni_log = {"Tarih": datetime.now(), "Soru": soru, "Durum": "Anahtar eşleşti ama senaryo yok", "Kullanıcı": kullanici if kullanici else "-"}
    else:
        st.warning("🤖 Bu soruya dair kayıtlı bir bilgi bulunamadı.")
        yeni_log = {"Tarih": datetime.now(), "Soru": soru, "Durum": "Eşleşme bulunamadı", "Kullanıcı": kullanici if kullanici else "-"}

    # Log'a yaz
    logs = pd.concat([logs, pd.DataFrame([yeni_log])], ignore_index=True)
    logs.to_excel(LOG_PATH, index=False)
