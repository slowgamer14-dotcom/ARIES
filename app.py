import streamlit as st
import google.generativeai as genai
import base64
import asyncio
import edge_tts

# 1. CONFIGURAÇÃO DO APP
st.set_page_config(page_title="Aries v2.5", page_icon="♈", layout="wide")

# 2. UI/UX: NEON, RESPONSIVIDADE E BOTÃO DE VOZ NA PONTA
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* Layout Mobile */
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
        .avatar-img { width: 100px !important; height: 100px !important; }
    }

    /* Avatar Aries */
    .avatar-container { display: flex; justify-content: center; margin-bottom: 15px; }
    .avatar-img {
        width: 140px; height: 140px;
        border-radius: 50%;
        border: 2px solid #ff4b4b;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.3);
        object-fit: cover;
    }

    /* Cards de Analytics */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border-left: 3px solid #ff4b4b;
        margin-bottom: 10px;
    }

    /* Botão de Voz na Ponta do Chat */
    .voice-toggle-container {
        position: fixed;
        bottom: 85px;
        right: 25px;
        z-index: 999;
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
        b64 = base64.b64encode(audio_content).decode()
        st.markdown(f'<audio autoplay style="display:none"><source src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)
    except: pass

# 4. MOTOR GEMINI 2.5
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        system_instruction="Você é Aries, uma IA v2.5. Técnica e direta. Foco em mistérios e estudos. Responda apenas como Aries."
    )
else:
    st.error("Configure a API Key nos Secrets.")

# --- BOTÃO DE VOZ FLUTUANTE NA PONTA DO CHAT ---
with st.container():
    st.markdown('<div class="voice-toggle-container">', unsafe_allow_html=True)
    st.session_state.voz_ativa = st.toggle("🔊", value=True, help="Ligar/Desligar Voz da Aries")
    st.markdown('</div>', unsafe_allow_html=True)

# --- INTERFACE ---
col_sidebar, col_main = st.columns([1, 2.5])

with col_sidebar:
    st.markdown("""<div class="avatar-container"><img src="https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/aries_avatar.png" class="avatar-img"></div>""", unsafe_allow_html=True)
    
    tabs = st.tabs(["📊 Analytics", "🎬 Edição"])
    
    with tabs[0]: # Analytics
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        canal_link = st.text_input("Link do Canal:", placeholder="https://youtube.com/...")
        if st.button("Escanear"):
            # Exemplo de exibição de dados extraídos pelo link
            st.divider()
            st.metric("Inscritos", "14.582", "+142")
            st.metric("Total Views", "1.240.300", "+5.2k")
            st.caption("Dados atualizados via Core 2.5")
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]: # Edição
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.selectbox("Modo de Corte", ["Shorts (9:16)", "Vídeo Longo (16:9)"])
        st.button("Renderizar")
        st.markdown('</div>', unsafe_allow_html=True)

with col_main:
    if "messages" not in st.session_state: st.session_state.messages = []
    
    # Histórico de Chat
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

# INPUT
if prompt := st.chat_input("Diga algo para Aries..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with col_main:
        with st.chat_message("user"): st.markdown(prompt)
    
    try:
        response = model.generate_content(prompt)
        txt = response.text
        with col_main:
            with st.chat_message("assistant"): st.markdown(txt)
        st.session_state.messages.append({"role": "assistant", "content": txt})
        aries_fala(txt)
    except:
        st.error("Falha no Core 2.5.")



