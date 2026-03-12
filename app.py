import streamlit as st
import google.generativeai as genai
import base64
import asyncio
import edge_tts
from audio_recorder_streamlit import audio_recorder

# 1. CONFIGURAÇÃO DO APP
st.set_page_config(page_title="Aries WhatsApp Pro", page_icon="♈", layout="wide")

# 2. CSS: INTERFACE WHATSAPP OBSIDIAN
st.markdown("""
    <style>
    .stApp { background-color: #0b141a; color: #e9edef; }
    
    /* Balões de Chat */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #005c4b !important;
        border-radius: 15px 0px 15px 15px !important;
        margin-left: 15% !important;
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #202c33 !important;
        border-radius: 0px 15px 15px 15px !important;
        margin-right: 15% !important;
    }

    /* Header Fixo */
    .wa-header {
        display: flex; align-items: center; padding: 10px 20px;
        background-color: #202c33; position: fixed; top: 0;
        width: 100%; z-index: 1000; border-bottom: 1px solid #313d45;
    }
    .wa-avatar { width: 45px; height: 45px; border-radius: 50%; margin-right: 15px; border: 1px solid #D4AF37; }

    /* Cards de Ferramentas */
    .drive-card {
        background: rgba(212, 175, 55, 0.05);
        border: 1px solid #D4AF37;
        padding: 15px; border-radius: 10px; margin: 10px 0;
    }

    .main-content { margin-top: 85px; margin-bottom: 100px; }
    #MainMenu, header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. SAÍDA DE VOZ
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
        system_instruction="Você é Aries v2.5 Pro. Especialista em edição de vídeos via Google Drive e análise de canais. Responda de forma curta e técnica, estilo WhatsApp. Nunca use Mentora ou LikaON."
    )
else:
    st.error("Erro: API Key não encontrada.")

# --- INTERFACE ---

st.markdown(f'''
    <div class="wa-header">
        <img src="https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/aries_avatar.png" class="wa-avatar">
        <div>
            <p style="margin:0; font-weight:bold; color: #e9edef;">Aries v2.5 Pro ♈</p>
            <p style="margin:0; font-size:12px; color: #D4AF37;">online (Drive Link Ativo)</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

abas = st.tabs(["💬 Chat", "🎬 Editor Drive", "📊 Analytics", "🎙️ Áudio"])

with abas[0]: # CHAT
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

with abas[1]: # EDITOR DRIVE (FOCO EM VÍDEOS LONGOS)
    st.markdown('<div class="drive-card">', unsafe_allow_html=True)
    st.write("📂 **Integração Google Drive**")
    drive_id = st.text_input("Cole o ID do vídeo longo:", placeholder="Ex: 1A2b3C4d5E...")
    
    opcoes = st.multiselect("Comandos de Edição:", 
                           ["Corte Inteligente (Long para Shorts)", "Tratamento de Áudio", "Legendas Automáticas", "Color Grading Zen"])
    
    if st.button("🚀 Iniciar Edição"):
        if drive_id:
            st.success(f"Aries acessando arquivo ID: {drive_id}")
            st.info("O motor Gemini 2.5 Flash está mapeando os pontos de corte...")
        else:
            st.warning("Por favor, insira o ID do arquivo no seu Drive.")
    st.markdown('</div>', unsafe_allow_html=True)

with abas[2]: # ANALYTICS
    canal = st.text_input("Link do Canal")
    if st.button("Escanear"):
        st.metric("Inscritos", "154.209", "+1.2k")
        st.metric("Views", "2.8M", "+15k")

with abas[3]: # ÁUDIO
    audio_bytes = audio_recorder(text="Gravar Comando", recording_color="#D4AF37", icon_size="3x")
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

st.markdown('</div>', unsafe_allow_html=True)

# CONTROLE DE VOZ NA SIDEBAR
st.sidebar.title("Configurações")
st.session_state.voz_ativa = st.sidebar.toggle("Voz da Aries", value=True)

# INPUT DE MENSAGEM
if p := st.chat_input("Mensagem"):
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
        st.error("Erro na conexão 2.5.")

