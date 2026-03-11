import streamlit as st
import requests

# 1. Configurações da Página
st.set_page_config(page_title="Aries AI - LikaON Empress", page_icon="♈", layout="wide")

# --- LINKS DAS IMAGENS (RAW) ---
url_fundo = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/fundo.jpg.png"
url_sidebar = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/sidebar.jpg.png"

# 2. Visual Neon Aries (CSS)
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("{url_fundo}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{
        background-image: url("{url_sidebar}");
        background-size: cover;
        border-right: 2px solid #ff4b4b;
    }}
    .stChatMessage {{
        background-color: rgba(14, 17, 23, 0.85) !important;
        border-radius: 15px;
        padding: 15px;
        border: 1px solid rgba(255, 75, 75, 0.4);
        margin-bottom: 10px;
    }}
    .stMetric {{ 
        background-color: rgba(30, 37, 46, 0.9); 
        padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; 
    }}
    div.stButton > button:first-child {{
        background-color: #ff4b4b; color: white; border-radius: 20px; 
        border: none; box-shadow: 0 0 15px #ff4b4b; width: 100%; transition: 0.3s;
    }}
    div.stButton > button:hover {{ box-shadow: 0 0 25px #ff4b4b; transform: scale(1.02); }}
    </style>
    """, unsafe_allow_html=True)

# 3. Chaves de Segurança
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Erro: Adicione GEMINI_API_KEY nos Secrets do Streamlit.")

MODELO = "gemini-2.5-flash"

# Personalidade Expandida
INSTRUCAO = (
    "Seu nome é Aries. Você é a empresária e editora-chefe do canal LikaON. "
    "Sua personalidade é feminina, decidida e sarcástica. "
    "Você domina o nicho de mistérios, Resident Evil e GTA. "
    "Analise dados de Analytics ou roteiros com rigor. Seja uma mentora de elite."
)

# --- SIDEBAR ---
with st.sidebar:
    st.title("📊 Status do Canal")
    st.info("Copie os dados do seu YouTube Studio e cole no chat para análise.")
    st.markdown("---")
    st.caption("Aries AI v2.5 - LikaON Empress")

# --- CONTEÚDO PRINCIPAL ---
st.title("♈ Aries AI - Central de Comando")

tab1, tab2 = st.tabs(["💬 Estratégia e Chat", "🎬 Script Lab"])

# ABA 1: CHAT
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Fale com a Aries ou cole seus dados..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={CHAVE_GEMINI}"
        
        payload = {
            "contents": [
                {"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} 
                for m in st.session_state.messages
            ],
            "system_instruction": {"parts": [{"text": INSTRUCAO}]},
            "generationConfig": {"temperature": 0.8}
        }

        with st.chat_message("assistant"):
            try:
                response = requests.post(url, json=payload)
                resultado = response.json()
                if 'candidates' in resultado:
                    resposta = resultado['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(resposta)
                    st.session_state.messages.append({"role": "assistant", "content": resposta})
                else:
                    st.error(f"Erro na API: {resultado}")
            except Exception as e:
                st.error(f"Falha de conexão: {e}")

# ABA 2: ROTEIROS
with tab2:
    st.subheader("🎬 Estúdio de Criação")
    st.write("Precisa de uma ideia matadora para o canal de mistérios?")
    if st.button("Gerar Gancho de Vídeo"):
        st.success("Aries diz: Comece o vídeo revelando algo que o espectador achava que era verdade, mas é mentira.")

