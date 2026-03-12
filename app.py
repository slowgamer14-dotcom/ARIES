import streamlit as st
import google.generativeai as genai
import base64
import asyncio
import edge_tts
from audio_recorder_streamlit import audio_recorder

# 1. CONFIGURAÇÃO DO APP
st.set_page_config(page_title="Aries v2.5 Pro", page_icon="♈", layout="wide")

# 2. CSS: DESIGN PREMIUM GLASSMORPHISM
st.markdown("""
    <style>
    /* Fundo Base Obsidiana */
    .stApp {
        background: radial-gradient(circle at top right, #1a1a1a, #050505);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Estilo Glass */
    .wa-header {
        display: flex; align-items: center; padding: 15px 25px;
        background: rgba(25, 25, 25, 0.8);
        backdrop-filter: blur(10px);
        position: fixed; top: 0; width: 100%;
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
        z-index: 1000;
    }
    .wa-avatar { 
        width: 50px; height: 50px; border-radius: 50%; 
        border: 2px solid #D4AF37; margin-right: 15px;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
    }

    /* Balões de Chat Glassmorphism */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background: rgba(0, 92, 75, 0.4) !important;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px 20px 0px 20px !important;
        margin-left: 15% !important;
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background: rgba(40, 40, 40, 0.6) !important;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(212, 175, 55, 0.1) !important;
        border-radius: 20px 20px 20px 0px !important;
        margin-right: 15% !important;
    }

    /* Cards e Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #888; }
    .stTabs [data-baseweb="tab--active"] { color: #D4AF37 !important; border-bottom-color: #D4AF37 !important; }

    .tool-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(212, 175, 55, 0.1);
        padding: 25px; border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    /* Customização de Inputs */
    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 10px !important;
    }

    .main-content { margin-top: 100px; margin-bottom: 100px; }
    #MainMenu, header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. LÓGICA DE VOZ (SAÍDA)
def aries_voz(texto):
    if not st.session_state.get("voz_ativa", True): return
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

# 4. MOTOR GEMINI 2.5 FLASH (OBRIGATÓRIO)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction="Você é Aries v2.5 Pro. IA de elite técnica. Especialista em edição de vídeos via Drive e canais de mistério. Estilo WhatsApp Premium. Identifique-se apenas como Aries."
    )
else:
    st.error("Chave API ausente.")

# --- INTERFACE ---
st.markdown(f'''
    <div class="wa-header">
        <img src="https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/aries_avatar.png" class="wa-avatar">
        <div>
            <p style="margin:0; font-weight:bold; color: #e9edef; font-size: 18px;">Aries v2.5 Pro</p>
            <p style="margin:0; font-size:12px; color: #D4AF37; letter-spacing: 1px;">CORE 2.5 ACTIVE</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

abas = st.tabs(["💬 Chat", "🎬 Drive Editor", "📊 Analytics", "🎙️ Rec"])

with abas[0]: # CHAT
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

with abas[1]: # EDITOR DRIVE
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#D4AF37;'>📂 Video ID Processing</h3>", unsafe_allow_html=True)
    drive_id = st.text_input("Cole o ID do Google Drive:", placeholder="ID do vídeo longo...")
    if st.button("🚀 Iniciar Edição 2.5"):
        if drive_id:
            st.success("Aries vinculada ao arquivo.")
            st.info("Mapeando pontos de retenção para cortes de Shorts...")
    st.markdown('</div>', unsafe_allow_html=True)

with abas[2]: # ANALYTICS
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.write("📈 **Canal Tracker**")
    st.text_input("Link do Canal:")
    col1, col2 = st.columns(2)
    col1.metric("Inscritos", "154.209", "+142")
    col2.metric("Visualizações", "2.8M", "+5.2k")
    st.markdown('</div>', unsafe_allow_html=True)

with abas[3]: # GRAVADOR
    st.write("Pressione para falar:")
    audio_bytes = audio_recorder(text="", recording_color="#D4AF37", icon_size="3x", neutral_color="#444")
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

st.markdown('</div>', unsafe_allow_html=True)

# SIDEBAR CONFIGS
st.sidebar.markdown("<h2 style='color:#D4AF37;'>Configurações</h2>", unsafe_allow_html=True)
st.session_state.voz_ativa = st.sidebar.toggle("Voz da Aries", value=True)

# 5. LÓGICA DE MENSAGENS
if p := st.chat_input("Diga algo para Aries..."):
    st.session_state.messages.append({"role": "user", "content": p})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    try:
        response = model.generate_content(st.session_state.messages[-1]["content"])
        txt = response.text
        st.session_state.messages.append({"role": "assistant", "content": txt})
        aries_voz(txt)
        st.rerun()
    except:
        st.error("Core 2.5 Offline.")

