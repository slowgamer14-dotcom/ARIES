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
