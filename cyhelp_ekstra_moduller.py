import streamlit as st

def mobil_uyumlu_tema():
    st.markdown("""
        <style>
            .block-container {
                padding: 1rem 2rem;
                max-width: 100% !important;
            }
            body, input, textarea {
                font-size: 16px !important;
            }
            .stButton>button {
                width: 100%;
                padding: 0.75rem;
            }
            .stTextInput>div>div>input {
                font-size: 16px !important;
                padding: 0.5rem;
            }
        </style>
    """, unsafe_allow_html=True)


def kullanici_bilgilendirme_mesaji():
    st.markdown("""
    <div style="background-color:#f0f8ff;padding:10px;border-radius:10px;border:1px solid #dcdcdc">
        📢 <strong>Bilgilendirme:</strong> Lütfen karşılaştığınız problemi detaylı yazın. Örnek: <em>"giriş yapamıyorum", "ruhsat görünmüyor"</em>
    </div>
    """, unsafe_allow_html=True)


def logo_baslik_alani():
    st.markdown("""
    <div style="text-align:center;">
        <img src="https://em-content.zobj.net/source/microsoft-teams/363/brain_1f9e0.png" width="80"/>
        <h1 style="color:#333;margin-top:0;">CYHELP | Yapay Zeka Destekli<br>VAVA İş Akış Asistanı</h1>
    </div>
    """, unsafe_allow_html=True)


def toast_mesaj(mesaj, renk="#4BB543"):
    st.markdown(f"""
    <div style="position:fixed;bottom:20px;right:20px;background-color:{renk};color:white;padding:10px 20px;border-radius:5px;box-shadow:2px 2px 10px rgba(0,0,0,0.3);z-index:9999;">
        ✅ {mesaj}
    </div>
    """, unsafe_allow_html=True)
