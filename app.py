import streamlit as st
import requests
import googleapiclient.discovery
import googleapiclient.http
from moviepy.editor import VideoFileClip
import google.generativeai as genai
import os
import io
import json
import time
import base64
import asyncio
import edge_tts

# 1. Configurações da Página
st.set_page_config(page_title="Aries AI - LikaON Empress", page_icon="♈", layout="wide")

# --- ESTILO VISUAL NEON (Ajustado para o Checkbox) ---
url_fundo = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/fundo.jpg.png"
url_sidebar = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/sidebar.jpg.png"

st.markdown(f"""
    <style>
    .stApp {{ 
        background-image: url("{url_fundo}"); 
        background-size: cover; 
        background-attachment: fixed; 
    }}
    [data-testid="stSidebar"] {{ 
        background-image: url("{url_sidebar}"); 
        background-size: cover; 
        border-right: 2px solid #ff4b4b; 
    }}
    .stChatMessage {{ 
        background-color: rgba(14, 17, 23, 0.85) !important; 
        border-radius: 15px; 
        border: 1px solid #ff4b4b; 
        margin-bottom: 10px; 
    }}
    div.stButton > button {{ 
        background-color: #ff4b4b; 
        color: white; 
        border-radius: 20px; 
        box-shadow: 0 0 10px #ff4b4b; 
        width: 100%; 
        font-weight: bold; 
        transition: 0.3s; 
    }}
    div.stButton > button:hover {{ 
        transform: scale(1.02); 
        background-color: #ff3333; 
    }}
    .stMetric {{ 
        background-color: rgba(0,0,0,0.6); 
        padding: 10px; 
        border-radius: 10px; 
        border: 1px solid #ff4b4b; 
    }}
    /* Estilo Neon para o Checkbox de Voz */
    div[data-testid="stCheckbox"] {{
        background-color: rgba(255, 75, 75, 0.1);
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #ff4b4b;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Voz (Edge-TTS Grátis)
def aries_fala(texto):
    # O SEGREDO: Verifica se o checkbox está ativo no session_state
    if not st.session_state.get("permitir_voz", True):
        return
        
    try:
        VOZ = "pt-BR-FranciscaNeural"
        async def generate_voice():
            communicate = edge_tts.Communicate(texto, VOZ)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data
            
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_content = loop.run_until_complete(generate_voice())
        audio_b64 = base64.b64encode(audio_content).decode()
        
        # Renderiza o player invisível que toca automaticamente
        st.markdown(
            f'<audio autoplay style="display:none"><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>', 
            unsafe_allow_html=True
        )
    except: 
        pass

# 3. Inicialização das APIs e Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "inscritos" not in st.session_state: st.session_state.inscritos = 0
if "views" not in st.session_state: st.session_state.views = 0

try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_DRIVE = st.secrets["GOOGLE_DRIVE_API_KEY"]
    CHAVE_YOUTUBE = st.secrets["YOUTUBE_API_KEY"]
    genai.configure(api_key=CHAVE_GEMINI)
except:
    st.error("⚠️ Erro: Chaves API não configuradas nos Secrets!")

MODELO_25 = "gemini-2.5-flash"
INSTRUCAO = "Você é Aries, mentora do canal LikaON. Sofisticada, direta e especialista em mistérios e Resident Evil."

# --- SIDEBAR (MÉTRICAS E CONTROLE) ---
with st.sidebar:
    st.title("📊 Painel LikaON")
    
    # BOTÃO PARA LIGAR/DESLIGAR VOZ
    st.session_state.permitir_voz = st.checkbox("🎙️ Ativar Voz da Aries", value=True)
    
    st.markdown("---")
    
    def buscar_stats():
        try
