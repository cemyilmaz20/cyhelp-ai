from io import BytesIO
import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="CYHELP", page_icon="🧠")
st.markdown("### 🧠 CYHELP | Yapay Zeka Destekli VAVA İş Akış Asistanı")

if "admin_user" not in st.session_state:
    st.session_state["admin_user"] = False

try:
    df = pd.read_excel("veri.xlsx")
except:
    df = pd.DataFrame(columns=["Anahtar Kelime", "Senaryo", "Açıklama", "Çözüm", "Sorumlu", "Görsel"])

log_dosyasi = "soru_loglari.xlsx"
if os.path.exists(log_dosyasi):
    logs = pd.read_excel(log_dosyasi)
else:
    logs = pd.DataFrame(columns=["Tarih", "Soru", "Durum", "Kullanıcı"])

soru = st.text_input("📝 Sorunuzu yazın (örnek: sistem dondu, giriş yapamıyorum...)")
kullanici_adi = st.text_input("👤 Kullanıcı adınız (isteğe bağlı):", key="kullanici")

if soru.strip().lower() == "cyadminacil":
    with st.expander("🔐 Yetkili girişi yapılıyor..."):
        admin_kullanici = st.text_input("👤 Kullanıcı Adı", key="admin_kadi")
        admin_sifre = st.text_input("🔑 Şifre", type="password", key="admin_sifre")
        if admin_kullanici == "cmyvava" and admin_sifre == "12345":
            st.success("✅ Giriş başarılı. Loglar aşağıda:")
            st.session_state["admin_user"] = True
        elif admin_kullanici and admin_sifre:
            st.error("❌ Hatalı kullanıcı adı veya şifre")

def yakala(cumle):
    cumle = cumle.lower()
    for kelime in df["Anahtar Kelime"].dropna().unique():
        if str(kelime).lower() in cumle:
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
        st.warning("⚠️ Hata ile ilgili görsel bulunamadı")

def log_ekle(soru, durum, kullanici):
    global logs
    yeni_kayit = {
        "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Soru": soru,
        "Durum": durum,
        "Kullanıcı": kullanici if kullanici else "-"
    }
    logs = pd.concat([logs, pd.DataFrame([yeni_kayit])], ignore_index=True)
    logs.to_excel(log_dosyasi, index=False)

if soru and soru.strip().lower() != "cyadminacil" and not st.session_state["admin_user"]:
    bulunan = yakala(soru)
    if bulunan:
        senaryolar = df[df["Anahtar Kelime"].str.lower() == bulunan.lower()]
        if not senaryolar.empty:
            st.info(f"🧠 '{bulunan}' ile ilgili {len(senaryolar)} çözüm bulundu:")
            secim = st.selectbox("Lütfen neyi kastettiğinizi seçin:", senaryolar["Senaryo"].tolist())
            secilen = senaryolar[senaryolar["Senaryo"] == secim].iloc[0]
            senaryo_goster(secilen)
            log_ekle(soru, "Eşleşme bulundu", kullanici_adi)
        else:
            st.warning("⚠️ Eşleşen anahtar kelime bulundu ama senaryo bilgisi eksik.")
            log_ekle(soru, "Anahtar eşleşti ama senaryo yok", kullanici_adi)
    else:
        st.warning("🤖 Bu soruya dair kayıtlı bir bilgi bulunamadı.")
        log_ekle(soru, "Eşleşme bulunamadı", kullanici_adi)

# ========== ADMIN PANEL ==========
if st.session_state["admin_user"]:
    st.markdown("### 📊 Soru Logları")
    st.success("✅ Giriş başarılı. Loglar aşağıda:")
    st.dataframe(logs, use_container_width=True)

    def to_excel_bytes(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

    excel_bytes = to_excel_bytes(logs)
    st.download_button("📥 Excel olarak indir", data=excel_bytes, file_name="loglar.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if st.button("🗑️ Logları sıfırla"):
        logs = pd.DataFrame(columns=["Tarih", "Soru", "Durum", "Kullanıcı"])
        if os.path.exists(log_dosyasi):
            os.remove(log_dosyasi)
        st.success("✅ Loglar temizlendi.")

    if st.button("🚪 Oturumu Kapat"):
        st.session_state.pop("admin_user", None)
        st.rerun()
