import streamlit as st
import requests
import googleapiclient.discovery

# 1. Configurações da Página
st.set_page_config(page_title="Aries AI - LikaON Empress", page_icon="♈", layout="wide")

# --- LINKS DAS IMAGENS (Ajustados para o formato RAW do GitHub) ---
# Note que adicionei 'raw' e removi 'blob' para o Streamlit conseguir acessar o arquivo real
url_fundo = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/fundo.jpg.png"
url_sidebar = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/sidebar.jpg.png"

# 2. CSS Customizado com as Imagens de Fundo
st.markdown(f"""
    <style>
    /* Imagem de Fundo Principal */
    .stApp {{
        background-image: url("{url_fundo}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* Imagem de Fundo da Barra Lateral */
    [data-testid="stSidebar"] {{
        background-image: url("{url_sidebar}");
        background-size: cover;
        background-position: center;
        border-right: 2px solid #ff4b4b;
    }}

    /* Estilização dos blocos para garantir legibilidade sobre o fundo */
    .stChatMessage {{
        background-color: rgba(14, 17, 23, 0.85) !important;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }}

    .stMetric {{ 
        background-color: rgba(30, 37, 46, 0.9); 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #ff4b4b; 
    }}

    /* Botão Neon */
    div.stButton > button:first-child {{
        background-color: #ff4b4b; color: white; border-radius: 20px; 
        border: none; box-shadow: 0 0 15px #ff4b4b; width: 100%; transition: 0.3s;
    }}
    div.stButton > button:hover {{ box-shadow: 0 0 25px #ff4b4b; transform: scale(1.02); }}

    /* Abas */
    .stTabs [data-baseweb="tab-list"] {{ gap: 24px; }}
    .stTabs [data-baseweb="tab"] {{ 
        height: 50px; background-color: rgba(30, 37, 46, 0.9); 
        border-radius: 10px 10px 0 0; color: white; padding: 10px 20px;
    }}
    .stTabs [aria-selected="true"] {{ background-color: #ff4b4b !important; }}
    </style>
    """, unsafe_allow_html=True)

# 3. Puxar as chaves dos Secrets
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_YOUTUBE = st.secrets["YOUTUBE_API_KEY"]
except:
    st.error("Erro: Verifique as chaves nos Secrets do Streamlit.")

MODELO = "gemini-1.5-flash" # Atualizado para a versão estável atual

# Personalidade da Aries
INSTRUCAO = (
    "Seu nome é Aries. Você é a empresária e editora-chefe do canal LikaON. "
    "Sua personalidade é feminina, decidida, inteligente e um pouco sarcástica. "
    "Você foca em resultados para YouTube e Instagram, entende de jogos de terror e GTA. "
    "Seu tom é de uma mentora de sucesso: elegante e direta."
)

# --- SIDEBAR ---
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

tab1, tab2 = st.tabs(["💬 Chat com Aries", "🎬 Editor de Vídeo"])

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
            except: st.error("Aries está processando dados, tente em um minuto.")

# ABA 2: EDITOR
with tab2:
    st.subheader("🎬 Estúdio de Edição")
    st.info("O módulo de processamento está aguardando seus clipes de GTA e Resident Evil.")

