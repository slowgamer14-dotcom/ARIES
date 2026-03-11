import streamlit as st
import requests
import googleapiclient.discovery

# 1. Configurações da Página
st.set_page_config(page_title="Aries AI - LikaON Empress", page_icon="♈", layout="wide")

# 2. CSS Customizado para o Visual Dark/Neon
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 2px solid #ff4b4b; }
    .stMetric { background-color: #1e252e; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
    div.stButton > button:first-child {
        background-color: #ff4b4b; color: white; border-radius: 20px; 
        border: none; box-shadow: 0 0 15px #ff4b4b; width: 100%; transition: 0.3s;
    }
    div.stButton > button:hover { box-shadow: 0 0 25px #ff4b4b; transform: scale(1.02); }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; white-space: pre-wrap; background-color: #1e252e; 
        border-radius: 10px 10px 0 0; color: white; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #ff4b4b !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Puxar as chaves dos Secrets
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_YOUTUBE = st.secrets["YOUTUBE_API_KEY"]
except:
    st.error("Erro: Verifique as chaves nos Secrets.")

MODELO = "gemini-2.5-flash"

# Personalidade Feminina: Aries
INSTRUCAO = (
    "Seu nome é Aries. Você é a empresária e editora-chefe do canal LikaON. "
    "Sua personalidade é feminina, decidida, inteligente e um pouco sarcástica. "
    "Você é focada em resultados e crescimento no YouTube/Instagram. "
    "Você entende muito de jogos de terror (RE, Silent Hill) e GTA. "
    "Seu tom é de uma mentora de sucesso: elegante, direta e incentivadora."
)

# --- SIDEBAR (PAINEL DE CONTROLE) ---
with st.sidebar:
    st.title("📊 Painel LikaON")
    if st.button("🔄 Consultar Estatísticas"):
        try:
            youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=CHAVE_YOUTUBE)
            request = youtube.channels().list(part="statistics,snippet", forHandle="@LikaON3")
            response = request.execute()
            if response.get('items'):
                canal = response['items'][0]
                st.metric("Inscritos", f"{int(canal['statistics']['subscriberCount']):,}")
                st.metric("Total de Views", f"{int(canal['statistics']['viewCount']):,}")
                st.metric("Vídeos", canal['statistics']['videoCount'])
            else: st.warning("Canal não encontrado.")
        except: st.error("Erro na conexão YouTube.")
    
    st.markdown("---")
    st.caption("Aries AI - Versão Empress 2.5")

# --- CONTEÚDO PRINCIPAL ---
st.title("✨ Aries AI - LikaON Empress")

tab1, tab2, tab3 = st.tabs(["💬 Chat com Aries", "🎬 Editor de Vídeo",)

# ABA 1: CHAT
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Como vamos dominar o YouTube hoje?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={CHAVE_GEMINI}"
        payload = {
            "system_instruction": {"parts": [{"text": INSTRUCAO}]},
            "contents": [{"role": "user" if m["role"] == "user" else "model", 
                          "parts": [{"text": m["content"]}]} for m in st.session_state.messages]
        }

        with st.chat_message("assistant"):
            try:
                response = requests.post(url, json=payload)
                resultado = response.json()
                resposta = resultado['candidates'][0]['content']['parts'][0]['text']
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})
            except: st.error("Aries está ocupada agora, tente em um minuto.")

# ABA 2: EDITOR (Simulação)
with tab2:
    st.subheader("🎬 Estúdio de Edição")
    st.info("O módulo MoviePy está pronto para processar seus clipes de GTA e Resident Evil.")
    # Aqui vai o código de upload que passamos antes

