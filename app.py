import streamlit as st
import requests
import googleapiclient.discovery

# 1. Configurações da Página
st.set_page_config(page_title="Aries AI - LikaON Empress", page_icon="♈", layout="wide")

# --- LINKS DAS IMAGENS (Certifique-se que os nomes no GitHub estão idênticos) ---
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
    </style>
    """, unsafe_allow_html=True)

# 3. Chaves de Segurança
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_YOUTUBE = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    st.error("Erro: Verifique as chaves nos Secrets do Streamlit.")

# --- MODELO GEMINI 2.5 FLASH OBRIGATÓRIO ---
MODELO = "gemini-2.5-flash"

INSTRUCAO = (
    "Seu nome é Aries. Você é a mentora e empresária do canal LikaON. "
    "Sua personalidade é feminina, sofisticada, decidida e estratégica. "
    "Você é uma líder nata: não é rude, mas é direta e focada em métricas. "
    "Você domina nichos de mistério, terror e games. "
    "Seu objetivo é transformar o canal no maior do Brasil."
)

# --- SIDEBAR (Analytics de volta) ---
with st.sidebar:
    st.title("📊 Painel de Controle")
    if st.button("🔄 Sincronizar Analytics"):
        try:
            youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=CHAVE_YOUTUBE)
            # Ajuste o handle conforme necessário
            request = youtube.channels().list(part="statistics,snippet", forHandle="@LikaON3")
            response = request.execute()
            if response.get('items'):
                canal = response['items'][0]
                st.metric("Inscritos", f"{int(canal['statistics']['subscriberCount']):,}")
                st.metric("Total de Views", f"{int(canal['statistics']['viewCount']):,}")
                st.metric("Vídeos", canal['statistics']['videoCount'])
            else:
                st
