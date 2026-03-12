import streamlit as st
import requests
import google.generativeai as genai
import base64
import asyncio
import edge_tts
import os

# --- 1. CONFIGURAÇÃO RESPONSIVA E TÍTULO ---
st.set_page_config(
    page_title="Aries AI",
    page_icon="♈",
    layout="wide",  # "wide" permite o uso de colunas responsivas
    initial_sidebar_state="collapsed" # Sidebar recolhida por defeito para mobile
)

# --- 2. CSS CUSTOMIZADO PARA DESIGN RESPONSIVO E EFEITO GLOW ---
st.markdown("""
    <style>
    /* Estilos Gerais (Dark Mode) */
    .stApp {
        background-color: #050505;
        color: #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Configurações Responsivas (Media Queries) */
    @media (max-width: 768px) {
        /* No Telemóvel, as colunas são empilhadas verticalmente */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        [data-testid="stColumn"] {
            width: 100% !important;
            margin-bottom: 20px;
        }
    }

    /* Avatar do Avatar Holográfico com Efeito de Brilho */
    .avatar-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 20px;
        margin-bottom: 30px;
    }
    
    .avatar-img {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        border: 2px solid #ff4b4b;
        box-shadow: 0 0 25px rgba(255, 75, 75, 0.6);
        object-fit: cover;
    }

    /* Balões de Chat Estilo Minimalista (Mais largos no mobile) */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
        border: none !important;
        margin-bottom: 12px;
    }

    /* Input de Comando (Estilo Mobile) */
    div[data-testid="stChatInput"] {
        padding: 15px;
    }

    /* Botões e Inputs com Estilo Neon Subtil */
    .stButton > button, .stTextInput input {
        background-color: transparent;
        color: #ff4b4b;
        border: 1px solid #ff4b4b;
        border-radius: 5px;
        transition: 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #ff4b4b;
        color: white;
        box-shadow: 0 0 10px #ff4b4b;
    }
    
    /* Esconder elementos desnecessários */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE VOZ (GRÁTIS E DIRETA) ---
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

# --- 4. INICIALIZAÇÃO DA IA ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    # Instrução limpa: apenas "Aries"
    INSTRUCAO = "Você é Aries. Uma IA técnica, direta e sofisticada. Foco: Canais Dark e suporte ao criador (futuro Bombeiro)."
except:
    st.error("Configure a GEMINI_API_KEY nos Secrets.")

# --- 5. INTERFACE UNIFICADA (PC E CELULAR) ---

# Título Centralizado
st.markdown("<h2 style='text-align: center;'>Aries AI</h2>", unsafe_allow_html=True)

# Layout Responsivo: Duas Colunas (Avatar + Chat)
col_avatar, col_chat = st.columns([1, 2.5])

# COLUNA DO AVATAR (Fica no TOPO no Mobile)
with col_avatar:
    # Exibição do Avatar (Usa a tua imagem preferida aqui)
    st.markdown(f"""
        <div class="avatar-container">
            <img src="https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/aries_avatar.png" class="avatar-img">
        </div>
        """, unsafe_allow_html=True)

# COLUNA DO CHAT (Fica ABAIXO do Avatar no Mobile)
with col_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Área de Mensagens
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# Input de Comando (Fica fixo na parte inferior)
if p := st.chat_input("Comando..."):
    st.session_state.messages.append({"role": "user", "content": p})
    # Atualiza a área de chat antes de chamar a IA
    with col_chat:
        with st.chat_message("user"):
            st.markdown(p)
    
    # Chama o Gemini
    try:
        # Envia o contexto da conversa
        chat = model.start_chat(history=[
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
            for m in st.session_state.messages[:-1]
        ])
        response = chat.send_message(p)
        txt = response.text
        # Adiciona a resposta à área de chat
        with col_chat:
            with st.chat_message("assistant"):
                st.markdown(txt)
        st.session_state.messages.append({"role": "assistant", "content": txt})
        aries_fala(txt)
    except Exception as e:
        st.error("Erro na conexão com a Aries.")


