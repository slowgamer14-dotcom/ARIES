import streamlit as st
import google.generativeai as genai
import time
import os
import re
import base64
import asyncio
import edge_tts
from moviepy.editor import VideoFileClip

# 1. CONFIGURAÇÃO DE INTERFACE
st.set_page_config(page_title="Aries v2.5 Pro", page_icon="♈", layout="wide")

# Estilo LikaON (Obsidian & Gold)
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #0b141a, #050505); color: #e9edef; }
    .tool-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(212, 175, 55, 0.1);
        padding: 25px; border-radius: 15px; margin-bottom: 20px;
    }
    .wa-header {
        display: flex; align-items: center; padding: 15px 25px;
        background: rgba(32, 44, 51, 0.9); backdrop-filter: blur(15px);
        border-bottom: 1px solid rgba(212, 175, 55, 0.3); margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZAÇÃO DO MOTOR 2.5
MODELO_25 = "gemini-2.5-flash" 
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("⚠️ Erro: GEMINI_API_KEY não configurada.")

# --- UI HEADER ---
st.markdown(f'''
    <div class="wa-header">
        <div style="width:48px; height:48px; background:#D4AF37; border-radius:50%; margin-right:15px;"></div>
        <div>
            <p style="margin:0; font-weight:bold; color: #e9edef;">Aries v2.5 Pro ♈</p>
            <p style="margin:0; font-size:11px; color: #D4AF37;">Core Gemini 2.5 Ativo | Editor LikaON</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# 3. DEFINIÇÃO DAS ABAS (RESOLVE O NAMEERROR)
abas = st.tabs(["💬 Chat 2.5", "🎬 Editor de Gameplay", "📊 Analytics"])

# --- ABA 1: CHAT ---
with abas[0]:
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

# --- ABA 2: EDITOR (COM CORTE FÍSICO) ---
with abas[1]:
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#D4AF37;'>🎬 Editor de Sustos Resident Evil</h3>", unsafe_allow_html=True)
    
    video_file = st.file_uploader("Upload da Gameplay (Até 1GB):", type=['mp4', 'mkv', 'mov'])
    
    if video_file:
        st.info(f"📁 Arquivo pronto: {video_file.name}")
        
        if st.button("🚀 Aries 2.5: Analisar e Cortar"):
            with st.spinner("Aries 2.5 assistindo ao vídeo..."):
                temp_orig = "input_original.mp4"
                with open(temp_orig, "wb") as f:
                    f.write(video_file.getbuffer())
                
                try:
                    # Upload para a IA
                    uploaded = genai.upload_file(path=temp_orig)
                    while uploaded.state.name == "PROCESSING":
                        time.sleep(10)
                        uploaded = genai.get_file(uploaded.name)
                    
                    # Análise do susto
                    model = genai.GenerativeModel(MODELO_25)
                    prompt = "Identifique o susto neste vídeo. Responda apenas o tempo no formato MM:SS e nada mais."
                    res = model.generate_content([uploaded, prompt])
                    
                    # Extração do tempo
                    match = re.search(r'(\d{1,2}:\d{2})', res.text)
                    if match:
                        tempo_susto = match.group(1)
                        st.success(f"🎯 Susto mapeado em: {tempo_susto}")
                        
                        # Processo de Corte
                        m, s = map(int, tempo_susto.split(':'))
                        inicio = max(0, (m * 60) + s - 3)
                        fim = inicio + 10
                        
                        output_clip = "susto_pronto.mp4"
                        with VideoFileClip(temp_orig) as video:
                            clipe = video.subclip(inicio, fim)
                            clipe.write_videofile(output_clip, codec="libx264", audio_codec="aac")
                        
                        with open(output_clip, "rb") as f:
                            st.download_button("📥 BAIXAR CLIPE DO SUSTO", f, file_name="susto_likaon.mp4")
                    else:
                        st.warning("IA não encontrou um tempo exato. Resposta: " + res.text)
                
                except Exception as e:
                    st.error(f"Erro: {e}")
                finally:
                    if os.path.exists(temp_orig): os.remove(temp_orig)
    st.markdown('</div>', unsafe_allow_html=True)

# --- ABA
