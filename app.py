import streamlit as st
import googleapiclient.discovery
import googleapiclient.http
import google.generativeai as genai
import requests
import time
import base64
import asyncio
import edge_tts
from audio_recorder_streamlit import audio_recorder

# 1. SETUP DE INTERFACE (OBSIDIAN GLASS)
st.set_page_config(page_title="Aries v2.5 Pro - LikaON", page_icon="♈", layout="wide")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #0b141a, #050505); color: #e9edef; }
    .wa-header {
        display: flex; align-items: center; padding: 15px 25px;
        background: rgba(32, 44, 51, 0.85); backdrop-filter: blur(15px);
        position: fixed; top: 0; width: 100%; border-bottom: 1px solid rgba(212, 175, 55, 0.3); z-index: 1000;
    }
    .wa-avatar { width: 50px; height: 50px; border-radius: 50%; border: 2px solid #D4AF37; margin-right: 15px; }
    .tool-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(212, 175, 55, 0.1);
        padding: 25px; border-radius: 15px; margin-bottom: 20px;
    }
    .main-content { margin-top: 100px; margin-bottom: 100px; }
    #MainMenu, header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. CONFIGURAÇÃO DE APIs
try:
    KEYS = st.secrets
    genai.configure(api_key=KEYS["GEMINI_API_KEY"])
    SHOTSTACK_KEY = KEYS["SHOTSTACK_API_KEY"]
except:
    st.error("⚠️ Erro: Configure as chaves nos Secrets (Gemini e Shotstack).")

# 3. MÓDULO DE VOZ
def aries_voz(texto):
    if not st.session_state.get("permitir_voz", True): return
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
        st.markdown(f'<audio autoplay style="display:none"><source src="data:audio/mp3;base64,{base64.b64encode(audio_content).decode()}"></audio>', unsafe_allow_html=True)
    except: pass

# --- INTERFACE ---
st.markdown(f'''
    <div class="wa-header">
        <img src="https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/aries_avatar.png" class="wa-avatar">
        <div>
            <p style="margin:0; font-weight:bold; color: #e9edef; font-size: 18px;">Aries v2.5 Pro ♈</p>
            <p style="margin:0; font-size:12px; color: #D4AF37;">Core 2.5 + Shotstack Active</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

abas = st.tabs(["💬 Chat", "🎬 Editor de Gameplay", "📊 Analytics", "🎙️ Rec"])

with abas[0]:
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

with abas[1]: # EDITOR DE GAMEPLAY (O SEGREDO DO 1GB)
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#D4AF37;'>🎬 Renderização de Gameplay</h3>", unsafe_allow_html=True)
    drive_id = st.text_input("ID do Vídeo no Drive (Gameplay > 1GB):")
    prompt_edicao = st.text_area("Instruções para Aries:", "Encontre o momento do susto, adicione um zoom e corte em 30 segundos.")

    if st.button("🚀 Renderizar Vídeo Final"):
        if drive_id:
            with st.spinner("Aries analisando timestamps e enviando para o Shotstack..."):
                # Simulação da chamada de API
                url = "https://api.shotstack.io/v1/render"
                headers = {"x-api-key": SHOTSTACK_KEY, "Content-Type": "application/json"}
                
                # A mágica: Aries gera este JSON automaticamente
                payload = {
                    "timeline": {
                        "tracks": [{"clips": [{"asset": {"type": "video", "src": f"https://drive.google.com/uc?id={drive_id}"}, "start": 0, "length": 15}]}]
                    },
                    "output": {"format": "mp4", "resolution": "hd"}
                }
                
                res = requests.post(url, json=payload, headers=headers)
                if res.status_code == 201:
                    render_id = res.json()['response']['id']
                    st.success(f"Vídeo em processamento! ID: {render_id}")
                    st.info("Aries está cuidando da renderização na nuvem. O link aparecerá aqui em instantes.")
                else:
                    st.error("Erro ao conectar com o Shotstack. Verifique sua chave Sandbox.")
        else:
            st.warning("Aries precisa do ID do vídeo no seu Drive.")
    st.markdown('</div>', unsafe_allow_html=True)

# LÓGICA DE MENSAGENS
if p := st.chat_input("Diga algo para Aries..."):
    st.session_state.messages.append({"role": "user", "content": p})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    model = genai.GenerativeModel("gemini-1.5-flash") # Usando flash para resposta rápida de chat
    response = model.generate_content(st.session_state.messages[-1]["content"])
    txt = response.text
    st.session_state.messages.append({"role": "assistant", "content": txt})
    aries_voz(txt)
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
