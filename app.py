import streamlit as st
import google.generativeai as genai
import base64
import asyncio
import edge_tts
from audio_recorder_streamlit import audio_recorder # Necessário adicionar ao requirements.txt

# 1. CONFIGURAÇÃO DO APP
st.set_page_config(page_title="Aries v2.5 Pro", page_icon="♈", layout="wide")

# 2. ESTILO OBSIDIAN ZEN
st.markdown("""
    <style>
    .stApp { background-color: #0D0D0D; color: #E0E0E0; }
    
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
        .avatar-img { width: 90px !important; height: 90px !important; }
    }

    .avatar-container { display: flex; justify-content: center; margin-bottom: 20px; }
    .avatar-img {
        width: 130px; height: 130px;
        border-radius: 50%;
        border: 1px solid #D4AF37;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.2);
        object-fit: cover;
    }

    .tool-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(212, 175, 55, 0.1);
        margin-bottom: 15px;
    }

    /* Controle de Voz na Ponta */
    .voice-control {
        position: fixed;
        bottom: 95px;
        right: 25px;
        z-index: 1001;
        background: #1A1A1A;
        padding: 8px;
        border-radius: 50%;
        border: 1px solid #D4AF37;
    }

    .stChatMessage { background-color: rgba(255, 255, 255, 0.02) !important; border-radius: 15px !important; }
    #MainMenu, footer, header {visibility: hidden;}
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

# 4. CONFIGURAÇÃO OBRIGATÓRIA GEMINI 2.5 FLASH
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction="Você é Aries v2.5 Pro. IA técnica e sofisticada. Ajude com edição de vídeo e estudos. Responda apenas como Aries."
    )
else:
    st.error("Chave API ausente.")

# --- CONTROLES FLUTUANTES ---
st.markdown('<div class="voice-control">', unsafe_allow_html=True)
st.session_state.voz_ativa = st.toggle("🔊", value=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- INTERFACE PRO ---
col_tools, col_main = st.columns([1.2, 2.3])

with col_tools:
    st.markdown('<div class="avatar-container"><img src="https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/aries_avatar.png" class="avatar-img"></div>', unsafe_allow_html=True)
    
    menu = st.tabs(["🎙️ Áudio", "📊 Analytics", "🎬 Editor"])
    
    with menu[0]: # ABA DE ÁUDIO (NOVA)
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.write("**Falar com Aries**")
        audio_bytes = audio_recorder(
            text="Toque para gravar",
            recording_color="#D4AF37",
            neutral_color="#E0E0E0",
            icon_size="2x",
        )
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            st.info("Áudio capturado. Aries está processando...")
            # Aqui você pode integrar o Whisper ou o próprio Gemini para transcrever
        st.markdown('</div>', unsafe_allow_html=True)

    with menu[1]: # ANALYTICS
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        canal = st.text_input("Link/Nome do Canal")
        if st.button("Escanear"):
            st.metric("Inscritos", "154.209", "+1.2k")
            st.metric("Views", "2.8M", "+15k")
        st.markdown('</div>', unsafe_allow_html=True)

    with menu[2]: # EDITOR
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.button("✂️ Cortar Shorts")
        st.button("📝 Legendar")
        st.markdown('</div>', unsafe_allow_html=True)

with col_main:
    if "messages" not in st.session_state: st.session_state.messages = []
    chat_box = st.container(height=500)
    with chat_box:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

# INPUT DE TEXTO
if p := st.chat_input("Comando para Aries..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with chat_box:
        with st.chat_message("user"): st.markdown(p)
    
    try:
        response = model.generate_content(p)
        txt = response.text
        with chat_box:
            with st.chat_message("assistant"): st.markdown(txt)
        st.session_state.messages.append({"role": "assistant", "content": txt})
        aries_voz(txt)
    except:
        st.error("Erro no Core 2.5.")
