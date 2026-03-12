import streamlit as st
import google.generativeai as genai
import requests
import time
import os
import base64
import asyncio
import edge_tts
from audio_recorder_streamlit import audio_recorder

# 1. SETUP DE INTERFACE (ESTILO WHATSAPP OBSIDIAN)
st.set_page_config(page_title="Aries v2.5 Pro", page_icon="♈", layout="wide")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #0b141a, #050505); color: #e9edef; }
    .wa-header {
        display: flex; align-items: center; padding: 15px 25px;
        background: rgba(32, 44, 51, 0.9); backdrop-filter: blur(15px);
        position: fixed; top: 0; width: 100%; border-bottom: 1px solid rgba(212, 175, 55, 0.3); z-index: 1000;
    }
    .wa-avatar { width: 48px; height: 48px; border-radius: 50%; border: 2px solid #D4AF37; margin-right: 15px; }
    .tool-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(212, 175, 55, 0.1);
        padding: 25px; border-radius: 15px; margin-bottom: 20px;
    }
    .main-content { margin-top: 100px; margin-bottom: 100px; }
    #MainMenu, header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZAÇÃO E CHAVES
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    SHOTSTACK_KEY = st.secrets["SHOTSTACK_API_KEY"]
except:
    st.error("⚠️ Verifique suas chaves nos Secrets!")

# 3. MÓDULO DE VOZ DA ARIES
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

# --- HEADER ---
st.markdown(f'''
    <div class="wa-header">
        <img src="https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/aries_avatar.png" class="wa-avatar">
        <div>
            <p style="margin:0; font-weight:bold; color: #e9edef;">Aries v2.5 Pro ♈</p>
            <p style="margin:0; font-size:11px; color: #D4AF37;">Core Ativo | Limite 1GB</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

tabs = st.tabs(["💬 Chat Estratégico", "🎬 Editor de Gameplay", "📊 Analytics"])

with tabs[1]: # O EDITOR LIKAON
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#D4AF37;'>🎬 Editor Inteligente de Resident Evil</h3>", unsafe_allow_html=True)
    
    # Upload Direto (Agora aceitando até 1GB)
    video_file = st.file_uploader("Suba sua gameplay (MP4/MKV):", type=['mp4', 'mkv', 'mov'])
    
    if video_file:
        st.info(f"Arquivo recebido: {video_file.name} ({video_file.size / 1024**2:.1f} MB)")
        
        if st.button("🚀 Aries, Encontre os Melhores Momentos"):
            with st.spinner("Aries está assistindo ao seu vídeo para identificar sustos e ação..."):
                # Salva temporário para o Gemini analisar
                with open("gameplay_temp.mp4", "wb") as f:
                    f.write(video_file.getbuffer())
                
                # Upload para a IA (O Google processa na nuvem dele)
                video_ai = genai.upload_file(path="gameplay_temp.mp4")
                while video_ai.state.name == "PROCESSING":
                    time.sleep(2)
                    video_ai = genai.get_file(video_ai.name)
                
                # Gemini 2.5 analisa e decide os cortes
                model = genai.GenerativeModel("gemini-1.5-flash") # Usando Flash para velocidade
                prompt = "Analise este vídeo de gameplay. Identifique os momentos de maior tensão (gritos ou sustos). Retorne apenas o tempo de início e fim do melhor momento no formato: 00:00 - 00:30."
                res = model.generate_content([video_ai, prompt])
                
                st.success(f"Aries encontrou o destaque: {res.text}")
                aries_voz(f"Encontrei um momento excelente para o seu canal. Vou preparar o corte.")
                
                # Limpeza
                genai.delete_file(video_ai.name)
                os.remove("gameplay_temp.mp4")
    st.markdown('</div>', unsafe_allow_html=True)

# LÓGICA DE MENSAGENS (CHAT)
if p := st.chat_input("Diga algo para Aries..."):
    if "messages" not in st.session_state: st.session_state.messages = []
    st.session_state.messages.append({"role": "user", "content": p})
    st.rerun()

# Exibe mensagens e gera resposta... (mesma lógica do chat anterior)


