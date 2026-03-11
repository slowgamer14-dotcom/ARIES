import streamlit as st
import requests
import googleapiclient.discovery

# 1. Configurações da Página
st.set_page_config(page_title="Aries AI - LikaON Empress", page_icon="♈", layout="wide")

# --- LINKS CORRIGIDOS (Versão 'Raw' para o Streamlit aceitar) ---
url_fundo = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/fundo.jpg.png"
url_sidebar = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/sidebar.jpg.png"

# 2. CSS Customizado - AGORA COM AS IMAGENS INCLUÍDAS
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

    /* Ajuste de contraste para as mensagens do chat */
    .stChatMessage {{
        background-color: rgba(14, 17, 23, 0.8) !important;
        border-radius: 10px;
    }}

    /* Resto do seu CSS original */
    .stMetric {{ background-color: #1e252e; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; }}
    div.stButton > button:first-child {{
        background-color: #ff4b4b; color: white; border-radius: 20px; 
        border: none; box-shadow: 0 0 15px #ff4b4b; width: 100%; transition: 0.3s;
    }}
    div.stButton > button:hover {{ box-shadow: 0 0 25px #ff4b4b; transform: scale(1.02); }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 24px; }}
    .stTabs [data-baseweb="tab"] {{ 
        height: 50px; white-space: pre-wrap; background-color: #1e252e; 
        border-radius: 10px 10px 0 0; color: white; padding: 10px 20px;
    }}
    .stTabs [aria-selected="true"] {{ background-color: #ff4b4b !important; }}
    </style>
    """, unsafe_allow_html=True)

# 3. Puxar as chaves dos Secrets (Mantenha igual)
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_YOUTUBE = st.secrets["YOUTUBE_API_KEY"]
except:
    st.error("Erro: Verifique as chaves nos Secrets.")

# ... Resto do seu código (Personalidade, Sidebar e Tabs) permanece o mesmo ...
