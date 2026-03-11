import streamlit as st
import requests
import googleapiclient.discovery

# 1. Configurações da Página
st.set_page_config(page_title="Aries AI - LikaON Empress", page_icon="♈", layout="wide")

# --- LINKS DAS IMAGENS ---
url_fundo = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/fundo.jpg.png"
url_sidebar = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/sidebar.jpg.png"

# 2. Visual Neon Aries (CSS)
st.markdown(f"""
    <style>
    .stApp {{ background-image: url("{url_fundo}"); background-size: cover; background-position: center; background-attachment: fixed; }}
    [data-testid="stSidebar"] {{ background-image: url("{url_sidebar}"); background-size: cover; border-right: 2px solid #ff4b4b; }}
    .stChatMessage {{ background-color: rgba(14, 17, 23, 0.85) !important; border-radius: 15px; padding: 15px; border: 1px solid rgba(255, 75, 75, 0.4); margin-bottom: 10px; }}
    .stMetric {{ background-color: rgba(30, 37, 46, 0.9); padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; color: white; }}
    div.stButton > button:first-child {{ background-color: #ff4b4b; color: white; border-radius: 20px; border: none; box-shadow: 0 0 15px #ff4b4b; width: 100%; transition: 0.3s; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# 3. Chaves de Segurança
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_YOUTUBE = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    st.error("Erro: Verifique as chaves GEMINI_API_KEY e YOUTUBE_API_KEY nos Secrets.")

MODELO = "gemini-2.5-flash"
INSTRUCAO = "Seu nome é Aries, mentora estratégica do canal LikaON. Você é decidida, inteligente e focada em resultados."

# --- SIDEBAR (ONDE O BOTÃO FUNCIONA) ---
with st.sidebar:
    st.title("📊 Painel de Controle")
    
    # Lógica do Botão de Sincronização
    if st.button("🔄 Sincronizar Analytics"):
        try:
            youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=CHAVE_YOUTUBE)
            # Busca os dados pelo handle do seu canal
            request = youtube.channels().list(part="statistics,snippet", forHandle="@LikaON3")
            response = request.execute()
            
            if response.get('items'):
                stats = response['items'][0]['statistics']
                st.session_state.inscritos = stats['subscriberCount']
                st.session_state.views = stats['viewCount']
                st.success("Dados sincronizados!")
            else:
                st.warning("Canal não encontrado.")
        except Exception as e:
            st.error(f"Erro na conexão: {e}")

    # Exibição das métricas (só aparecem após clicar no botão)
    if 'inscritos' in st.session_state:
        st.metric("Inscritos", f"{int(st.session_state.inscritos):,}")
        st.metric("Views", f"{int(st.session_state.views):,}")
    
    st.markdown("---")
    st.caption("Aries AI v2.5 Flash - LikaON Empress")

# --- CONTEÚDO PRINCIPAL (CHAT) ---
st.title("✨ Aries AI - LikaON Empress")

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
        "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages],
        "system_instruction": {"parts": [{"text": INSTRUCAO}]}
    }

    with st.chat_message("assistant"):
        try:
            r = requests.post(url, json=payload)
            resposta = r.json()['candidates'][0]['content']['parts'][0]['text']
            st.markdown(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta})
        except:
            st.error("Erro ao falar com a Aries.")
