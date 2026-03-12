import streamlit as st
import google.generativeai as genai
import requests
import time
import os
import base64
import asyncio
import edge_tts

# 1. CONFIGURAÇÃO DE INTERFACE ULTRA PREMIUM
st.set_page_config(page_title="Aries v2.5 Pro", page_icon="♈", layout="wide")

# Estilo Obsidian Gold (WhatsApp Dark Mode Style)
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

# 2. INICIALIZAÇÃO DE APIs
try:
    # Definindo o modelo como a versão 2.5 experimental estável
    MODELO_25 = "gemini-2.5-flash-exp" 
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    SHOTSTACK_KEY = st.secrets["SHOTSTACK_API_KEY"]
except Exception as e:
    st.error("⚠️ Erro nas Chaves API. Verifique os Secrets do Streamlit.")

# 3. SISTEMA DE VOZ ARIES
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

# --- ESTRUTURA VISUAL ---
st.markdown(f'''
    <div class="wa-header">
        <img src="https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/aries_avatar.png" class="wa-avatar">
        <div>
            <p style="margin:0; font-weight:bold; color: #e9edef;">Aries v2.5 Pro ♈</p>
            <p style="margin:0; font-size:11px; color: #D4AF37;">Core 2.5 Ativo | Edição em Nuvem</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Criação das Abas (Padronizado como 'abas')
abas = st.tabs(["💬 Chat Estratégico", "🎬 Editor de Gameplay", "📊 Analytics"])

# --- ABA 1: CHAT ---
with abas[0]:
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

# --- ABA 2: EDITOR (COM CORREÇÃO DE MEMÓRIA E MODELO 2.5) ---
with abas[1]:
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#D4AF37;'>🎬 Central de Edição LikaON</h3>", unsafe_allow_html=True)
    
    video_file = st.file_uploader("Suba sua gameplay (Suporte até 1GB):", type=['mp4', 'mkv', 'mov'])
    
    if video_file:
        st.info(f"📁 Arquivo carregado: {video_file.name} ({video_file.size / 1024**2:.1f} MB)")
        
        if st.button("🚀 Aries 2.5: Analisar e Cortar Susto"):
            with st.spinner("Enviando vídeo para o processamento neural..."):
                # Salvando arquivo temporário
                temp_path = "gameplay_upload.mp4"
                with open(temp_path, "wb") as f:
                    f.write(video_file.getbuffer())
                
                try:
                    # Upload para a API do Google
                    video_ai = genai.upload_file(path=temp_path)
                    
                    # Loop de espera até o vídeo ficar ACTIVE
                    status_info = st.empty()
                    while video_ai.state.name == "PROCESSING":
                        status_info.warning("⏳ Aries está processando os frames... aguarde.")
                        time.sleep(8)
                        video_ai = genai.get_file(video_ai.name)
                    
                    if video_ai.state.name == "ACTIVE":
                        status_info.success("✅ Vídeo pronto para análise!")
                        
                        # Invocando o modelo 2.5
                        model = genai.GenerativeModel(MODELO_25)
                        prompt = "Analise esta gameplay de Resident Evil. Identifique o susto mais intenso. Retorne o tempo (00:00) e sugira um título 'Clickbait' para o canal LikaON."
                        
                        res = model.generate_content([video_ai, prompt])
                        st.markdown("### 🎯 Resultado da Análise Aries 2.5")
                        st.write(res.text)
                        
                        aries_voz("Corte identificado. O susto foi mapeado com sucesso para o canal LikaON.")
                    else:
                        st.error("Erro: O vídeo falhou no processamento do servidor.")
                        
                except Exception as err:
                    st.error(f"Erro no motor 2.5: {err}")
                finally:
                    # Limpando arquivos para não encher o servidor
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    else:
        st.write("Aguardando upload de gameplay para iniciar a edição...")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ABA 3: ANALYTICS ---
with abas[2]:
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.metric("Crescimento Projetado", "+15%", "YouTube SEO")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# LÓGICA DE MENSAGENS DO CHAT
if p := st.chat_input("Diga algo para Aries..."):
    st.session_state.messages.append({"role": "user", "content": p})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    model_chat = genai.GenerativeModel("gemini-1.5-flash")
    response = model_chat.generate_content(st.session_state.messages[-1]["content"])
    txt = response.text
    st.session_state.messages.append({"role": "assistant", "content": txt})
    aries_voz(txt)
    st.rerun()


