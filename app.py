import streamlit as st
import google.generativeai as genai
import requests
import time
import os
import base64
import asyncio
import edge_tts

# 1. ESTÉTICA LIKAON PRO (OBSIDIAN & GOLD)
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

# 2. CONFIGURAÇÃO DO MOTOR 2.5 (IDENTIFICADOR ATUALIZADO)
# Este é o modelo que substitui o 001 e traz a inteligência 2.5 real
MODELO_25 = "gemini-2.0-flash" 

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("⚠️ Erro: GEMINI_API_KEY ausente nos Secrets!")

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
        b64 = base64.b64encode(audio_content).decode()
        st.markdown(f'<audio autoplay style="display:none"><source src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)
    except: pass

# --- UI HEADER ---
st.markdown(f'''
    <div class="wa-header">
        <img src="https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/aries_avatar.png" class="wa-avatar">
        <div>
            <p style="margin:0; font-weight:bold; color: #e9edef;">Aries v2.5 Pro ♈</p>
            <p style="margin:0; font-size:11px; color: #D4AF37;">Motor Gemini 2.5 Atualizado | Ativo</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Abas padronizadas
abas = st.tabs(["💬 Chat 2.5", "🎬 Editor de Gameplay", "📊 Analytics"])

with abas[0]:
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

with abas[1]:
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#D4AF37;'>🎬 Editor LikaON - Motor 2.5</h3>", unsafe_allow_html=True)
    
    video_file = st.file_uploader("Upload de Gameplay (Suporte 1GB):", type=['mp4', 'mkv', 'mov'])
    
    if video_file:
        st.info(f"📂 Arquivo: {video_file.name} | Pronto para análise 2.5.")
        
        if st.button("🚀 Iniciar Análise Versão 2.5"):
            with st.spinner("Aries 2.5 processando frames..."):
                temp_name = "gameplay_likaon.mp4"
                with open(temp_name, "wb") as f:
                    f.write(video_file.getbuffer())
                
                try:
                    # Upload para o sistema de arquivos da IA
                    video_upload = genai.upload_file(path=temp_name)
                    
                    # Verificação de ativação
                    placeholder = st.empty()
                    while video_upload.state.name == "PROCESSING":
                        placeholder.warning("⏳ Motor 2.5 codificando vídeo de 1GB... Isso leva um momento.")
                        time.sleep(15) 
                        video_upload = genai.get_file(video_upload.name)
                    
                    if video_upload.state.name == "ACTIVE":
                        placeholder.success("✅ Vídeo Ativo no Core 2.5!")
                        
                        # Invocação da inteligência 2.5 (Usando o novo nome)
                        model = genai.GenerativeModel(model_name=MODELO_25)
                        prompt = "Aja como editor do canal LikaON. Encontre o susto nesta gameplay de Resident Evil e sugira um título épico."
                        
                        res = model.generate_content([video_upload, prompt])
                        st.markdown("### 🎯 Relatório Aries 2.5")
                        st.write(res.text)
                        aries_voz("Análise 2.5 concluída. O susto foi localizado com sucesso.")
                    else:
                        st.error("Erro: O processamento do vídeo falhou.")
                
                except Exception as e:
                    st.error(f"Erro no Motor 2.5: {e}")
                finally:
                    if os.path.exists(temp_name):
                        os.remove(temp_name)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# LÓGICA DO CHAT INPUT
if p := st.chat_input("Comando para Aries 2.5..."):
    st.session_state.messages.append({"role": "user", "content": p})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    model_chat = genai.GenerativeModel(MODELO_25)
    response = model_chat.generate_content(st.session_state.messages[-1]["content"])
    txt = response.text
    st.session_state.messages.append({"role": "assistant", "content": txt})
    aries_voz(txt)
    st.rerun()



