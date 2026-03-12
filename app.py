import streamlit as st
import google.generativeai as genai
import base64
import asyncio
import edge_tts

# 1. CONFIGURAÇÃO DA PÁGINA E RESPONSIVIDADE
st.set_page_config(page_title="Aries AI", page_icon="♈", layout="wide")

# 2. DESIGN UNIFICADO (PC/CELULAR) - CSS NEON
st.markdown("""
    <style>
    /* Fundo Escuro Absoluto */
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* Ajuste para Celular */
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
        .avatar-img { width: 120px !important; height: 120px !important; }
    }

    /* Avatar Holográfico Central */
    .avatar-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    .avatar-img {
        width: 180px; height: 180px;
        border-radius: 50%;
        border: 2px solid #ff4b4b;
        box-shadow: 0 0 30px rgba(255, 75, 75, 0.5);
        object-fit: cover;
    }

    /* Chat Estilo 'Clean Glass' */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        margin-bottom: 10px;
    }

    /* Input fixo inferior */
    div[data-testid="stChatInput"] { padding: 15px; }
    
    /* Esconder menus padrão */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. LÓGICA DE VOZ (Aries Falando)
def aries_voz(texto):
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

# 4. CONFIGURAÇÃO GEMINI 2.5 FLASH
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # O modelo 'gemini-2.5-flash' é configurado via System Instruction
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", # Use 1.5-flash para máxima compatibilidade estável
        system_instruction="Você é Aries. Uma IA técnica e sofisticada. Suas respostas são diretas e focadas em tecnologia, mistérios e produtividade. Nunca use o nome LikaON ou o termo Mentora. Trate o usuário com foco em seus objetivos de canal e carreira."
    )
except:
    st.error("Erro: Verifique sua GEMINI_API_KEY nos Secrets.")

# --- INTERFACE ---

st.markdown("<h1 style='text-align: center; font-size: 24px;'>Aries v2.5</h1>", unsafe_allow_html=True)

# Divisão PC (Lado a Lado) / Celular (Empilhado)
col_personagem, col_conversa = st.columns([1, 2])

with col_personagem:
    st.markdown("""
        <div class="avatar-container">
            <img src="https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/aries_avatar.png" class="avatar-img">
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #ff4b4b;'>Aries Ativa</p>", unsafe_allow_html=True)

with col_conversa:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# Entrada de dados
if prompt := st.chat_input("Comando para Aries..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with col_conversa:
        with st.chat_message("user"): st.markdown(prompt)
    
    try:
        response = model.generate_content(prompt)
        txt = response.text
        with col_conversa:
            with st.chat_message("assistant"): st.markdown(txt)
        st.session_state.messages.append({"role": "assistant", "content": txt})
        aries_voz(txt)
    except:
        st.error("Conexão interrompida.")


