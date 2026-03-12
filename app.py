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
with abas[1]: # EDITOR COM UPLOAD DIRETO
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#D4AF37;'>🎬 Upload & Edição Direta</h3>", unsafe_allow_html=True)
    
    # Campo de Upload (Suporta até 200MB por padrão no Streamlit, expansível)
    video_file = st.file_uploader("Arraste sua gameplay aqui (MP4, MOV, AVI)", type=['mp4', 'mov', 'avi'])
    
    if video_file is not None:
        st.video(video_file) # Preview do vídeo que você subiu
        
        if st.button("🚀 Aries, Analisar e Editar"):
            with st.spinner("Aries está assistindo ao vídeo..."):
                # Salva o arquivo temporariamente
                with open("temp_video.mp4", "wb") as f:
                    f.write(video_file.getbuffer())
                
                # Envia para o Gemini 2.5 Flash
                video_ai = genai.upload_file(path="temp_video.mp4")
                
                # Espera o processamento do Google
                while video_ai.state.name == "PROCESSING":
                    time.sleep(2)
                    video_ai = genai.get_file(video_ai.name)
                
                # Aries gera os cortes baseada no vídeo real
                model = genai.GenerativeModel(MODELO_25)
                res = model.generate_content([video_ai, "Identifique o momento de maior tensão e sugira um corte de 30 segundos em formato JSON."])
                
                st.success("Análise concluída!")
                st.write(res.text)
                
                # Limpeza
                genai.delete_file(video_ai.name)
                os.remove("temp_video.mp4")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

