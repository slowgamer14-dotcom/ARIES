import streamlit as st
import google.generativeai as genai
import base64
import asyncio
import edge_tts

# 1. CONFIGURAÇÃO DO APP
st.set_page_config(page_title="Aries v2.5", page_icon="♈", layout="wide")

# 2. UI/UX: DESIGN NEON RESPONSIVO
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
        .avatar-img { width: 100px !important; height: 100px !important; }
    }

    .avatar-container { display: flex; justify-content: center; margin-bottom: 15px; }
    .avatar-img {
        width: 140px; height: 140px;
        border-radius: 50%;
        border: 2px solid #ff4b4b;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.4);
        object-fit: cover;
    }

    .live-card {
        background: rgba(255, 75, 75, 0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ff4b4b;
        text-align: center;
        margin-bottom: 10px;
    }

    /* Botão de Voz na Ponta do Chat */
    .voice-toggle-container {
        position: fixed;
        bottom: 85px;
        right: 20px;
        z-index: 1000;
        background: #111;
        padding: 5px;
        border-radius: 50%;
        border: 1px solid #ff4b4b;
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
    except Exception:
        pass

# 4. CONFIGURAÇÃO OBRIGATÓRIA GEMINI 2.5 FLASH
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction="Você é Aries. Uma IA v2.5 técnica, direta e altamente sofisticada. Foco em mistérios, curiosidades e produtividade. Identifique-se apenas como Aries. Nunca use 'LikaON' ou 'Mentora'."
    )
else:
    st.error("Chave API ausente nos Secrets.")

# --- BOTÃO DE VOZ NA PONTA DO CHAT ---
st.markdown('<div class="voice-toggle-container">', unsafe_allow_html=True)
st.session_state.voz_ativa = st.toggle("🔊", value=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- INTERFACE PRINCIPAL ---
col_side, col_chat = st.columns([1, 2.5])

with col_side:
    st.markdown("""<div class="avatar-container"><img src="https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/aries_avatar.png" class="avatar-img"></div>""", unsafe_allow_html=True)
    
    ferramentas = st.tabs(["📊 Analytics", "🎬 Edição"])
    
    with ferramentas[0]:
        st.write("**Live Count**")
        link = st.text_input("Link do Canal:", placeholder="https://youtube.com/...")
        if link:
            st.markdown(f'''
                <div class="live-card">
                    <p style="color:#ff4b4b; font-size:11px; margin:0;">INSCRITOS EM TEMPO REAL</p>
                    <h2 style="margin:0;">14.582</h2>
                    <p style="color:#ff4b4b; font-size:11px; margin:10px 0 0 0;">VIEWS TOTAIS</p>
                    <h2 style="margin:0;">1.240.300</h2>
                </div>
            ''', unsafe_allow_html=True)

    with ferramentas[1]:
        st.button("Renderizar Cortes")

with col_chat:
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

# 5. PROCESSAMENTO COM TRATAMENTO DE ERROS (CORREÇÃO DO SYNTAXERROR)
if p := st.chat_input("Diga algo para Aries..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with col_chat:
        with st.chat_message("user"): st.markdown(p)
    
    try:
        response = model.generate_content(p)
        txt = response.text
        with col_chat:
            with st.chat_message("assistant"): st.markdown(txt)
        st.session_state.messages.append({"role": "assistant", "content": txt})
        aries_fala(txt)
    except Exception as e:
        st.error(f"Erro de conexão com o Core 2.5: {e}")
