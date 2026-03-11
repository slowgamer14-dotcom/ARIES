import streamlit as st
import requests
import googleapiclient.discovery

# 1. Configurações da Página
st.set_page_config(page_title="Aries AI - LikaON Empress", page_icon="♈", layout="wide")

# --- LINKS DAS IMAGENS ---
url_fundo = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/fundo.jpg.png"
url_sidebar = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/sidebar.jpg.png"

# 2. CSS Customizado (Corrigido)
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
        background-position: center;
        border-right: 2px solid #ff4b4b;
    }}
    .stChatMessage {{
        background-color: rgba(14, 17, 23, 0.85) !important;
        border-radius: 15px;
        padding: 10px;
        border: 1px solid rgba(255, 75, 75, 0.3);
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

# 3. Puxar as chaves dos Secrets
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_YOUTUBE = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    st.error("Erro: Verifique as chaves nos Secrets do Streamlit.")

# --- MODELO GEMINI 2.5 FLASH ---
MODELO = "gemini-2.5-flash"

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
        except Exception: st.error("Erro na conexão YouTube.")
    
    st.markdown("---")
    st.caption("Aries AI - Versão Empress 2.5 Flash")

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
        with st.chat_message("user"):
            st.markdown(prompt)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={CHAVE_GEMINI}"
        
        payload = {
            "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages],
            "system_instruction": {"parts": [{"text": INSTRUCAO}]},
            "generationConfig": {"temperature": 0.8, "maxOutputTokens": 2048}
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
                st.error(f"Erro de conexão: {e}")

# ABA 2: EDITOR
with tab2:
    st.subheader("🎬 Estúdio de Edição")
    st.info("Módulo pronto para processar os vídeos do canal.")
