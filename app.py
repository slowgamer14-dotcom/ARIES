import streamlit as st
import google.generativeai as genai
import base64
import asyncio
import edge_tts

# 1. CONFIGURAÇÃO DO APP
st.set_page_config(page_title="Aries v2.5", page_icon="♈", layout="wide")

# 2. DESIGN RESPONSIVO E UI (PC/CELULAR)
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
        .avatar-img { width: 110px !important; height: 110px !important; }
    }

    .avatar-container { display: flex; justify-content: center; margin: 10px 0; }
    .avatar-img {
        width: 150px; height: 150px;
        border-radius: 50%;
        border: 2px solid #ff4b4b;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.3);
        object-fit: cover;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border-left: 3px solid #ff4b4b;
        margin-bottom: 15px;
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

# 4. CONFIGURAÇÃO GEMINI 2.5
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        system_instruction="Você é Aries. Uma IA v2.5 técnica e direta. Ajuda com vídeos de mistério e estudos. Identifique-se apenas como Aries."
    )
else:
    st.error("Chave API ausente.")

# --- SIDEBAR (CONTROLES) ---
with st.sidebar:
    st.title("♈ Aries v2.5")
    st.session_state.voz_ativa = st.toggle("Ativar Voz", value=True)
    if st.button("Limpar Histórico"):
        st.session_state.messages = []
        st.rerun()

# --- INTERFACE PRINCIPAL ---
col_left, col_right = st.columns([1, 2.5])

with col_left:
    st.markdown("""<div class="avatar-container"><img src="https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/aries_avatar.png" class="avatar-img"></div>""", unsafe_allow_html=True)
    
    # FERRAMENTAS
    tab_ana, tab_edit = st.tabs(["📊 Analytics", "🎬 Edição"])
    
    with tab_ana:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.write("**Análise de Canal por Link**")
        canal_link = st.text_input("Cole o link do YouTube aqui:", placeholder="https://youtube.com/@...")
        
        if st.button("Escanear Canal"):
            if canal_link:
                with st.spinner("Aries acessando metadados..."):
                    # Aqui entra a lógica de conexão futura. Por enquanto, a Aries simula a leitura.
                    st.success(f"Canal detectado.")
                    st.metric("Engajamento Estimado", "8.4%", "+1.2%")
                    st.write("📈 *Tendência de busca para este nicho: Alta*")
            else:
                st.warning("Insira um link válido.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_edit:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.write("**Workflow de Produção**")
        st.text_input("ID do Arquivo")
        st.selectbox("Prioridade de IA", ["Legendas Dinâmicas", "Color Grading", "Cortes Estratégicos"])
        if st.button("Processar Vídeo"):
            st.info("Iniciando renderização via Cloud...")
        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Comando..."):
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
        st.error("Conexão interrompida com o Core 2.5.")


