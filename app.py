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
    div.stButton > button:first-child {{
        background-color: #ff4b4b; color: white; border-radius: 20px; 
        border: none; box-shadow: 0 0 15px #ff4b4b; width: 100%; transition: 0.3s;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. Chaves de Segurança (Corrigido linha 45)
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_YOUTUBE = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    st.error("Erro: Verifique as chaves GEMINI_API_KEY e YOUTUBE_API_KEY nos Secrets do Streamlit.")

# --- MODELO GEMINI 2.5 FLASH ---
MODELO = "gemini-2.5-flash"

INSTRUCAO = (
    "Seu nome é Aries. Você é a mentora e empresária do canal LikaON. "
    "Sua personalidade é sofisticada, decidida e estratégica. "
    "Você domina o nicho de mistérios e games. Trate o usuário como um parceiro de elite."
)

# --- SIDEBAR (Analytics) ---
with st.sidebar:
    st.title("📊 Painel de Controle")
    if st.button("🔄 Sincronizar Analytics"):
        try:
            youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=CHAVE_YOUTUBE)
            request = youtube.channels().list(part="statistics,snippet", forHandle="@LikaON3")
            response = request.execute()
            if response.get('items'):
                canal = response['items'][0]
                st.metric("Inscritos", f"{int(canal['statistics']['subscriberCount']):,}")
                st.metric("Views", f"{int(canal['statistics']['viewCount']):,}")
                st.success("Dados sincronizados!")
            else:
                st.warning("Canal não encontrado.")
        except Exception as e:
            st.error(f"Erro na API do YouTube: {e}")
    
    st.markdown("---")
    st.caption("Aries AI v2.5 Flash - LikaON Empress")

# --- CONTEÚDO PRINCIPAL ---
st.title("✨ Aries AI - LikaON Empress")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada do Chat
if prompt := st.chat_input("Como vamos dominar o YouTube hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chamada para API do Gemini 2.5
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={CHAVE_GEMINI}"
    
    payload = {
        "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages],
        "system_instruction": {"parts": [{"text": INSTRUCAO}]},
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
    }

    with st.chat_message("assistant"):
        try:
            response = requests.post(url, json=payload)
            resultado = response.json()
            
            if 'candidates' in resultado and len(resultado['candidates']) > 0:
                resposta = resultado['candidates'][0]['content']['parts'][0]['text']
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})
            else:
                msg_erro = resultado.get('error', {}).get('message', 'Erro na resposta da API.')
                st.error(f"Aries encontrou um problema: {msg_erro}")
        except Exception as e:
            st.error(f"Erro de conexão com a Aries: {e}")

