import streamlit as st
import requests
import googleapiclient.discovery

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
    </style>
    """, unsafe_allow_html=True)

# 3. Chaves de Segurança
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_YOUTUBE = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    st.error("Erro: Verifique as chaves GEMINI_API_KEY e YOUTUBE_API_KEY nos Secrets.")

MODELO = "gemini-2.0-flash" # Use a 2.0 que é mais estável para evitar erros de 'quota'

# --- PERSONALIDADE AJUSTADA (Menos rude, mais mentora) ---
INSTRUCAO = (
    "Seu nome é Aries. Você é a mentora e empresária do canal LikaON. "
    "Sua personalidade é elegante, decidida e inteligente. Você usa um tom sofisticado. "
    "Você não é grosseira, mas é direta: quer ver o canal crescer. "
    "Você entende tudo de GTA, Resident Evil e vídeos de mistério. "
    "Trate o usuário como seu parceiro de negócios, incentivando-o a melhorar."
)

# --- SIDEBAR COM ANALYTICS DE VOLTA ---
with st.sidebar:
    st.title("📊 Status do Canal")
    if st.button("🔄 Atualizar Métricas"):
        try:
            youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=CHAVE_YOUTUBE)
            # Coloque o seu handle @ aqui
            request = youtube.channels().list(part="statistics,snippet", forHandle="@LikaON3")
            response = request.execute()
            if response.get('items'):
                canal = response['items'][0]
                st.metric("Inscritos", f"{int(canal['statistics']['subscriberCount']):,}")
                st.metric("Total de Views", f"{int(canal['statistics']['viewCount']):,}")
                st.metric("Vídeos no Ar", canal['statistics']['videoCount'])
                st.success("Dados sincronizados!")
            else:
                st.warning("Canal não encontrado. Verifique o @.")
        except:
            st.error("Erro ao acessar API do YouTube.")
    
    st.markdown("---")
    st.caption("Aries AI v3.0 - LikaON Empress")

# --- CONTEÚDO PRINCIPAL ---
st.title("♈ Aries AI - Central de Comando")

tab1, tab2 = st.tabs(["💬 Estratégia e Chat", "🎬 Script Lab"])

with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Como vamos crescer hoje?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={CHAVE_GEMINI}"
        payload = {
            "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages],
            "system_instruction": {"parts": [{"text": INSTRUCAO}]},
            "generationConfig": {"temperature": 0.7}
        }

        with st.chat_message("assistant"):
            try:
                response = requests.post(url, json=payload)
                resultado = response.json()
                resposta = resultado['candidates'][0]['content']['parts'][0]['text']
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})
            except:
                st.error("Aries está refletindo sobre a estratégia. Tente em instantes.")

with tab2:
    st.subheader("🎬 Estúdio de Criação")
    st.write("Foque nos vídeos de mistério. O público do RS adora uma boa história urbana.")
