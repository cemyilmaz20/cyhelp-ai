from datetime import datetime
import pandas as pd
import streamlit as st
import os
import io
from cyhelp_ekstra_moduller import *  # 👈 bu satırı ekliyorsun
st.set_page_config(page_title="CYHELP | VAVA Yapay Zeka Destekli Asistan", page_icon="🧠")
st.markdown("<h1 style='text-align: center;'>🧠 CYHELP | Yapay Zeka Destekli<br>VAVA İş Akış Asistanı</h1>", unsafe_allow_html=True)

EXCEL_LOG = "soru_loglari.xlsx"
EXCEL_DATA = "veri.xlsx"
ADMIN_KODU = "cyadminacil"
ADMIN_KULLANICI = "cmyvava"
ADMIN_SIFRE = "12345"

def oturumu_kapat():
    for key in ["admin_user", "sifre", "logs", "soru"]:
        st.session_state.pop(key, None)
    st.rerun()

def loglari_yukle():
    if os.path.exists(EXCEL_LOG):
        return pd.read_excel(EXCEL_LOG)
    return pd.DataFrame(columns=["Tarih", "Soru", "Durum", "Kullanıcı"])

def log_ekle(soru, durum, kullanici):
    logs = loglari_yukle()
    yeni_kayit = {
        "Tarih": turkiye_saati(),  # Saat düzeltildi
        "Soru": soru,
        "Durum": durum,
        "Kullanıcı": kullanici if kullanici else "-"
    }
    logs = pd.concat([logs, pd.DataFrame([yeni_kayit])], ignore_index=True)
    logs.to_excel(EXCEL_LOG, index=False)

def anahtar_bul(cumle, keywords):
    cumle = cumle.lower()
    for kelime in keywords:
        if kelime.lower() in cumle:
            return kelime
    return None

def senaryo_goster(row):
    st.subheader(f"📌 {row['Senaryo']}")
    st.markdown(f"**🔎 Açıklama:** {row['Açıklama']}")
    st.markdown(f"**🛠️ Çözüm:** {row['Çözüm']}")
    st.markdown(f"**👤 Sorumlu:** {row['Sorumlu']}")
    if pd.notna(row["Görsel"]) and row["Görsel"] != "":
        st.image(f"images/{row['Görsel']}", caption=row["Senaryo"])
    else:
        st.warning(f"⚠️ Hata ile ilgili görsel bulunamadı")

@st.cache_data
def veriyi_yukle():
    if os.path.exists(EXCEL_DATA):
        return pd.read_excel(EXCEL_DATA)
    else:
        return pd.DataFrame(columns=["Anahtar Kelime", "Senaryo", "Açıklama", "Çözüm", "Sorumlu", "Görsel"])

df = veriyi_yukle()

soru = st.text_input("📝 Sorunuzu yazın (örnek: sistem dondu, giriş yapamıyorum...):", key="soru")
kullanici_adi = st.text_input("👤 Kullanıcı adınız (isteğe bağlı):", key="kullanici")

if soru.strip().lower() == ADMIN_KODU.lower():
    with st.expander("🔐 Yetkili girişi yapılıyor..."):
        st.text_input("👤 Kullanıcı Adı", key="admin_user")
        st.text_input("🔑 Şifre", type="password", key="sifre")
        if st.session_state.get("admin_user") == ADMIN_KULLANICI and st.session_state.get("sifre") == ADMIN_SIFRE:
            st.success("✅ Giriş başarılı.")

            # Butonlarla işlem seçme
            secim = st.radio("🔧 Admin İşlemleri Seçin", ["Logları Gör", "Yeni Senaryo", "Senaryo Düzenle", "Sık Sorular"])

            if secim == "Logları Gör":
                logs = loglari_yukle()
                st.subheader("📊 Soru Logları")
                st.dataframe(logs, use_container_width=True)
                buffer = io.BytesIO()
                logs.to_excel(buffer, index=False, engine='openpyxl')
                buffer.seek(0)
                st.download_button("📥 Excel olarak indir", data=buffer, file_name="soru_loglari.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                if st.button("🗑️ Logları sıfırla"):
                    os.remove(EXCEL_LOG) if os.path.exists(EXCEL_LOG) else None
                    st.rerun()

            elif secim == "Yeni Senaryo":
                senaryo_ekle_formu()

            elif secim == "Senaryo Düzenle":
                senaryo_duzenle_paneli()

            elif secim == "Sık Sorular":
                sik_sorulan_kontrolu()

            if st.button("🚪 Oturumu Kapat"):
                oturumu_kapat()

        elif st.session_state.get("admin_user") and st.session_state.get("sifre"):
            st.error("❌ Hatalı kullanıcı adı veya şifre")

else:
    if soru:
        eslesen_kelime = anahtar_bul(soru, df["Anahtar Kelime"].unique())
        if eslesen_kelime:
            senaryolar = df[df["Anahtar Kelime"].str.lower() == eslesen_kelime.lower()]
            if not senaryolar.empty:
                st.info(f"🧠 Eşleşen kelime: '{eslesen_kelime}'")
                secim = st.selectbox("Lütfen neyi kastettiğinizi seçin:", senaryolar["Senaryo"].tolist())
                secilen = senaryolar[senaryolar["Senaryo"] == secim].iloc[0]
                senaryo_goster(secilen)
                log_ekle(soru, "Eşleşme bulundu", kullanici_adi)
                toast_bildirim("✅ Sorunuz başarıyla kaydedildi", "success")
            else:
                st.warning("⚠️ Eşleşen anahtar kelime bulundu ama senaryo bilgisi eksik.")
                log_ekle(soru, "Anahtar eşleşti ama senaryo yok", kullanici_adi)
                toast_bildirim("⚠️ Senaryo bulunamadı", "warning")
        else:
            st.warning("🤖 Bu soruya dair kayıtlı bir bilgi bulunamadı.")
            log_ekle(soru, "Eşleşme bulunamadı", kullanici_adi)
            toast_bildirim("⚠️ Eşleşme bulunamadı", "error")
