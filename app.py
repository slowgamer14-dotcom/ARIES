import streamlit as st
import google.generativeai as genai
import base64
import asyncio
import edge_tts
import time

# 1. CONFIGURAÇÃO DO APP
st.set_page_config(page_title="Aries v2.5", page_icon="♈", layout="wide")

# 2. UI/UX: NEON CARMESIM E BOTÃO DE VOZ NA PONTA
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* Ajustes Mobile */
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
        .avatar-img { width: 100px !important; height: 100px !important; }
    }

    .avatar-container { display: flex; justify-content: center; margin-bottom: 15px; }
    .avatar-img {
        width: 140px; height: 140px;
        border-radius: 50%;
        border: 2px solid #ff4b4b;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.4);
        object-fit: cover;
    }

    /* Live Count Estilizado */
    .live-card {
        background: rgba(255, 75, 75, 0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ff4b4b;
        text-align: center;
        margin-bottom: 10px;
    }

    /* Botão de Voz na Ponta do Chat (Fixed) */
    .voice-toggle-container {
        position: fixed;
        bottom: 85px;
        right: 20px;
        z-index: 1000;
        background: #111;
        padding: 5px;
        border-radius: 50%;
        border: 1px solid #ff4b4b;
    }

    .stChatMessage { background-color: rgba(255, 75, 75, 0.03) !important; border-radius: 12px !important; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. LÓGICA DE VOZ
def aries_fala(texto):
    if not st.session_state.get("voz_ativa", True):
        return
    try:
        async def generate():
            communicate = edge_tts.Communicate(texto, "pt-BR-FranciscaNeural")
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio": audio_data += chunk["data"]
            return audio_data
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_content = loop.run_until_complete(generate())
        b64 = base64.b64encode



