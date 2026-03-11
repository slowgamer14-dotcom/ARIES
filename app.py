import streamlit as st
import requests
import googleapiclient.discovery
import googleapiclient.http
from moviepy.editor import VideoFileClip
import os
import io

# 1. Configurações da Página
st.set_page_config(page_title="Aries AI - LikaON Empress", page_icon="♈", layout="wide")

# --- LINKS DAS IMAGENS (RAW) ---
url_fundo = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/fundo.jpg.png"
url_sidebar = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/sidebar.jpg.png"

# 2. Visual Neon Aries (CSS Otimizado)
st.markdown(f"""
    <style>
    .stApp {{ background-image: url("{url_fundo}"); background-size: cover; background-attachment: fixed; }}
    [data-testid="stSidebar"] {{ background-image: url("{url_sidebar}"); background-size: cover; border-right: 2px solid #ff4b4b; }}
    .stChatMessage {{ background-color: rgba(14, 17, 23, 0.85) !important; border-radius: 15px; border: 1px solid #ff4b4b; margin-bottom: 10px; }}
    .stMetric {{ background-color: rgba(30, 37, 46, 0.9); padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; }}
    div.stButton > button {{ background-color: #ff4b4b; color: white; border-radius: 20px; box-shadow: 0 0 10px #ff4b4b; width: 100%; transition: 0.3s; font-weight: bold; }}
    div.stButton > button:hover {{ transform: scale(1.02); background-color: #ff3333; }}
    .stTextInput > div > div > input {{ background-color: rgba(0,0,0,0.5); border: 1px solid #ff4b4b; color: white; }}
    </style>
    """, unsafe_allow_html=True)

# 3. Chaves de Segurança
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_YOUTUBE = st.secrets["YOUTUBE_API_KEY"]
    CHAVE_DRIVE = st.secrets["GOOGLE_DRIVE_API_KEY"]
except Exception:
    st.error("⚠️ Atenção: Verifique se todas as chaves (GEMINI, YOUTUBE e DRIVE) estão nos Secrets!")

MODELO = "gemini-2.5-flash"
INSTRUCAO = (
    "Seu nome é Aries. Mentora e estrategista do canal LikaON. "
    "Foco: Gameplay, mistérios e alta retenção. Seja sofisticada e direta."
)

# --- SIDEBAR: ANALYTICS ---
with st.sidebar:
    st.title("📊 Painel LikaON")
    if st.button("🔄 Sincronizar Analytics"):
        try:
            yt = googleapiclient.discovery.build("youtube", "v3", developerKey=CHAVE_YOUTUBE)
            r = yt.channels().list(part="statistics", forHandle="@LikaON3").execute()
            if r.get('items'):
                s = r['items'][0]['statistics']
                st.session_state.inscritos, st.session_state.views = s['subscriberCount'], s['viewCount']
                st.success("Métricas sincronizadas!")
            else: st.warning("Canal não encontrado.")
        except: st.error("Erro na API do YouTube.")
    
    if 'inscritos' in st.session_state:
        st.metric("Inscritos", f"{int(st.session_state.inscritos):,}")
        st.metric("Total Views", f"{int(st.session_state.views):,}")
    
    st.markdown("---")
    st.caption("Aries v2.5 Flash | Edição Cloud Ativa")

# --- CONTEÚDO PRINCIPAL ---
st.title("♈ Aries AI - Central de Comando")
tab1, tab2 = st.tabs(["💬 Chat de Estratégia", "☁️ Editor Google Drive"])

# ABA 1: CHAT INTELIGENTE
with tab1:
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("Como vamos dominar o YouTube hoje?"):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        url =
