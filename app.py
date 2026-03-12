import streamlit as st
import google.generativeai as genai
import base64
import asyncio
import edge_tts

# 1. CONFIGURAÇÃO DO APP
st.set_page_config(page_title="Aries v2.5", page_icon="♈", layout="wide")

# 2. DESIGN RESPONSIVO (CSS UNIFICADO)
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* Layout Adaptável */
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
        .avatar-img { width: 130px !important; height: 130px !important; }
    }

    /* Avatar Holográfico Aries */
    .avatar-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    .avatar-img {
        width: 170px; height: 170px;
        border-radius: 50%;
        border: 2px solid #ff4b4b;
        box-shadow: 0 0 25px rgba(255, 75, 75, 0.4);
        object-fit: cover;
    }

    /* Balão de Chat */
    .stChatMessage {
        background-color: rgba(255, 75, 75, 0.04) !important;
        border-radius: 12px !important;
    }

    /* Estética de Interface Limpa */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. LÓGICA DE VOZ
def aries_fala(texto):
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

# 4. CONFIGURAÇÃO ESPECÍFICA GEMINI 2.5 FLASH
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Configurando para a versão 2.5 Flash
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction="Você é Aries. Uma IA de última geração (v2.5). Técnica, direta e focada em resultados. Auxilia em canais Dark de mistério e rotinas de estudo. Identifique-se apenas como Aries."
    )
else:
    st.error("Chave API não configurada nos Secrets.")

# --- INTERFACE ---

st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>Aries v2.5</h2>", unsafe_allow_html=True)

# Colunas que se ajustam (PC Lado a Lado / Mobile Empilhado)
col_avatar, col_chat = st.columns([1, 2.5])

with col_avatar:
    st.markdown("""
        <div class="avatar-container">
            <img src="https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/aries_avatar.png" class="avatar-img">
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 11px; color: #ff4b4b; letter-spacing: 2px;'>SYSTEM 2.5 ACTIVE</p>", unsafe_allow_html=True)

with col_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# INPUT DE COMANDO
if prompt := st.chat_input("Comando..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with col_chat:
        with st.chat_message("user"): st.markdown(prompt)
    
    try:
        # Gerando resposta com o motor 2.5
        response = model.generate_content(prompt)
        txt = response.text
        with col_chat:
            with st.chat_message("assistant"): st.markdown(txt)
        st.session_state.messages.append({"role": "assistant", "content": txt})
        aries_fala(txt)
    except Exception as e:
        st.error("Erro de conexão com o Core 2.5. Verifique a API Key ou limite de uso.")

