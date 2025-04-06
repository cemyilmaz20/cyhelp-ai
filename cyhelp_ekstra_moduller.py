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

# Mevcut senaryoları gösterme ve düzenleme
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

# Logları yükleme
def loglari_yukle():
    if os.path.exists("soru_loglari.xlsx"):
        return pd.read_excel("soru_loglari.xlsx")
    return pd.DataFrame(columns=["Tarih", "Soru", "Durum", "Kullanıcı"])

# Log ekleme
def log_ekle(soru, durum, kullanici):
    logs = loglari_yukle()
    yeni_kayit = {
        "Tarih": turkiye_saati(),
        "Soru": soru,
        "Durum": durum,
        "Kullanıcı": kullanici if kullanici else "-"
    }
    logs = pd.concat([logs, pd.DataFrame([yeni_kayit])], ignore_index=True)
    logs.to_excel("soru_loglari.xlsx", index=False)

# Kullanıcının sorusuna uygun senaryo bulma
def anahtar_bul(cumle, keywords):
    cumle = cumle.lower()
    for kelime in keywords:
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
        st.image(f"images/{row['Görsel']}", caption=row["Senaryo"])
    else:
        st.warning(f"⚠️ Hata ile ilgili görsel bulunamadı")

# Veriyi yükleme
def veriyi_yukle():
    if os.path.exists("veri.xlsx"):
        return pd.read_excel("veri.xlsx")
    else:
        return pd.DataFrame(columns=["Anahtar Kelime", "Senaryo", "Açıklama", "Çözüm", "Sorumlu", "Görsel"])

# Ana uygulama başlatma
df = veriyi_yukle()
soru = st.text_input("📝 Sorunuzu yazın (örnek: sistem dondu, giriş yapamıyorum...):", key="soru")
kullanici_adi = st.text_input("👤 Kullanıcı adınız (isteğe bağlı):", key="kullanici")

if soru.strip().lower() == "cyadminacil":
    with st.expander("🔐 Yetkili girişi yapılıyor..."):
        st.text_input("👤 Kullanıcı Adı", key="admin_user")
        st.text_input("🔑 Şifre", type="password", key="sifre")
        if st.session_state.get("admin_user") == "cmyvava" and st.session_state.get("sifre") == "12345":
            st.success("✅ Giriş başarılı. Loglar aşağıda:")
            logs = loglari_yukle()
            st.subheader("📊 Soru Logları")
            st.dataframe(logs, use_container_width=True)

            buffer = io.BytesIO()
            logs.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)

            st.download_button(
            "📥 Excel olarak indir",
            data=buffer,
            file_name="soru_loglari.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            if st.button("🗑️ Logları sıfırla"):
                os.remove("soru_loglari.xlsx") if os.path.exists("soru_loglari.xlsx") else None
                st.rerun()

            if st.button("🚪 Oturumu Kapat"):
                for key in ["admin_user", "sifre", "logs", "soru"]:
                    st.session_state.pop(key, None)
                st.rerun()
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
