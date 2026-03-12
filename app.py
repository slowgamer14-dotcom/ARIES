import streamlit as st
import google.generativeai as genai
import base64
import asyncio
import edge_tts

# 1. CONFIGURAÇÃO DO APP
st.set_page_config(page_title="Aries v2.5", page_icon="♈", layout="wide")

# 2. DESIGN RESPONSIVO E UI CLEAN
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* Layout Adaptável */
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
        .avatar-img { width: 110px !important; height: 110px !important; }
    }

    /* Avatar Aries */
    .avatar-container { display: flex; justify-content: center; margin: 10px 0; }
    .avatar-img {
        width: 150px; height: 150px;
        border-radius: 50%;
        border: 2px solid #ff4b4b;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.3);
        object-fit: cover;
    }

    /* Estilização de Containers (Cards) */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border-left: 3px solid #ff4b4b;
        margin-bottom: 10px;
    }

    /* Chat */
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

# 4. CONFIGURAÇÃO GEMINI 2.5
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", # Mantendo flash pela velocidade no mobile
        system_instruction="Você é Aries. Uma IA v2.5 técnica e direta. Ajuda com vídeos de mistério e estudos para Bombeiro. Sem nomes como LikaON."
    )
else:
    st.error("Chave API ausente.")

# --- SIDEBAR (CONTROLES RÁPIDOS) ---
with st.sidebar:
    st.title("♈ Painel Aries")
    st.session_state.voz_ativa = st.toggle("Voz da Aries", value=True)
    st.divider()
    st.button("Limpar Conversa", on_click=lambda: st.session_state.update(messages=[]))

# --- INTERFACE PRINCIPAL ---
col_left, col_right = st.columns([1, 2.5])

with col_left:
    st.markdown("""<div class="avatar-container"><img src="https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/aries_avatar.png" class="avatar-img"></div>""", unsafe_allow_html=True)
    
    # ABA DE FERRAMENTAS (EDIÇÃO E ANALYTICS)
    tab_edit, tab_ana = st.tabs(["🎬 Edição", "📊 Analytics"])
    
    with tab_edit:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        video_id = st.text_input("ID do Vídeo (Drive/YT)")
        st.multiselect("Ações de Edição", ["Cortes Secos", "Legendas Auto", "Remover Silêncio", "Efeito Glitch"])
        if st.button("Iniciar Processamento"):
            st.info("Aries está processando o vídeo...")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_ana:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.write("**Desempenho Canal Dark**")
        st.metric("Inscritos", "14.5K", "+120")
        st.metric("Views (24h)", "3.2K", "+15%")
        if st.button("Gerar Relatório"):
            st.success("Relatório de tendências de mistério pronto.")
        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    if "messages" not in st.session_state: st.session_state.messages = []
    
    chat_container = st.container(height=400 if not st.session_state.get('is_mobile') else 300)
    with chat_container:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Comando para Aries..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with col_right:
        with st.chat_message("user"): st.markdown(prompt)
    
    try:
        response = model.generate_content(prompt)
        txt = response.text
        with col_right:
            with st.chat_message("assistant"): st.markdown(txt)
        st.session_state.messages.append({"role": "assistant", "content": txt})
        aries_fala(txt)
    except:
        st.error("Erro no Core 2.5.")


