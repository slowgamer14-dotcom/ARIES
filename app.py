import streamlit as st
import requests
import googleapiclient.discovery

# Configurações da Página
st.set_page_config(page_title="Aries AI - Laica 1", page_icon="♈")

# O JEITO CERTO: Puxar pelo nome que você salvou no Streamlit
# Se você salvou como GEMINI_API_KEY lá nos Secrets, use assim:
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_YOUTUBE = st.secrets["YOUTUBE_API_KEY"]
except:
    st.error("Erro: As chaves API não foram encontradas nos Secrets do Streamlit.")

MODELO = "gemini-1.5-flash" # Use o 1.5 que é mais estável para esse tipo de app

# Estilo do Aries (Personalidade de Empresário e Editor)
INSTRUCAO = (
    "Seu nome é Aries. Você é o empresário e editor do canal Laica 1. "
    "Seu tom é bem-humorado, direto e focado em crescimento no YouTube e Instagram. "
    "Você entende de jogos de terror (Resident Evil, Silent Hill) e GTA. "
    "Ajude o usuário a gerenciar o canal e a se preparar para o concurso de Bombeiro."
)

st.title("♈ Aries - Empresário LikaON")

# --- MÓDULO EMPRESÁRIO (SIDEBAR) ---
with st.sidebar:
    st.header("📊 Painel do Canal")
    if st.button("Consultar Stats do LikaON"):
        try:
            youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=CHAVE_YOUTUBE)
            request = youtube.channels().list(part="statistics,snippet", forHandle="@LikaON3")
            response = request.execute()
            
            if response['items']:
                canal = response['items'][0]
                nome = canal['snippet']['title']
                subs = canal['statistics']['subscriberCount']
                views = canal['statistics']['viewCount']
                vids = canal['statistics']['videoCount']
                
                st.success(f"Conectado: {nome}")
                st.metric("Inscritos", f"{int(subs):,}")
                st.metric("Total de Views", f"{int(views):,}")
                st.metric("Vídeos Postados", vids)
            else:
                st.warning("Canal não encontrado. Verifique o @handle.")
        except Exception as e:
            st.error(f"Erro no YouTube: {e}")

# --- CHAT DO ARIES ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Como vamos crescer o Laica 1 hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chamada para o Google Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={CHAVE_GEMINI}"
    payload = {
        "system_instruction": {"parts": {"text": INSTRUCAO}},
        "contents": [{"parts": [{"text": m["content"]} for m in st.session_state.messages]}]
    }

    with st.chat_message("assistant"):
        try:
            response = requests.post(url, json=payload)
            resultado = response.json()
            resposta_ia = resultado['candidates'][0]['content']['parts'][0]['text']
            st.markdown(resposta_ia)
            st.session_state.messages.append({"role": "assistant", "content": resposta_ia})
        except Exception as e:
            st.error(f"Erro no Aries: {e}")


