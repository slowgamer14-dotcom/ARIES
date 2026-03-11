import streamlit as st
import requests
import googleapiclient.discovery

# Configurações da Página
st.set_page_config(page_title="Aries AI", page_icon="♈")

# Puxa as chaves dos Secrets de forma segura
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_YOUTUBE = st.secrets["YOUTUBE_API_KEY"]
except Exception as e:
    st.error("Erro: Verifique se GEMINI_API_KEY e YOUTUBE_API_KEY estão nos Secrets do Streamlit.")

# MUDANÇA IMPORTANTE: Usando o modelo estável 1.5
MODELO = "gemini-1.5-flash-latest" 

INSTRUCAO = (
    "Seu nome é Aries. Você é o empresário e editor do canal LikaON. "
    "Seu tom é bem-humorado, direto e focado em crescimento no YouTube e Instagram. "
    "Você entende de jogos de terror (Resident Evil, Silent Hill) e GTA. "
    "Ajude o usuário com o canal e com o concurso de Bombeiro."
)

st.title("♈ Aries - Empresário LikaON")

# --- MÓDULO EMPRESÁRIO (SIDEBAR) ---
with st.sidebar:
    st.header("📊 Painel do Canal")
    if st.button("Consultar Stats do LikaON"):
        try:
            youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=CHAVE_YOUTUBE)
            # Ajustado para o seu novo handle @LikaON3
            request = youtube.channels().list(part="statistics,snippet", forHandle="@LikaON3")
            response = request.execute()
            
            if response.get('items'):
                canal = response['items'][0]
                nome = canal['snippet']['title']
                subs = canal['statistics']['subscriberCount']
                views = canal['statistics']['viewCount']
                
                st.success(f"Conectado: {nome}")
                st.metric("Inscritos", f"{int(subs):,}")
                st.metric("Total de Views", f"{int(views):,}")
            else:
                st.warning("Canal @LikaON3 não encontrado.")
        except Exception as e:
            st.error(f"Erro no YouTube: {e}")

# --- CHAT DO ARIES ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Como vamos crescer o LikaON hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chamada para o Google Gemini com verificação de erro
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={CHAVE_GEMINI}"
   # Novo formato de payload compatível com v1
    payload = {
    "system_instruction": {"parts": [{"text": INSTRUCAO}]},
    "contents": [
        {
            "role": "user" if m["role"] == "user" else "model",
            "parts": [{"text": m["content"]}]
        } for m in st.session_state.messages
    ]
}

    with st.chat_message("assistant"):
        try:
            response = requests.post(url, json=payload)
            resultado = response.json()
            
            # Aqui resolve o erro de 'candidates'
            if 'candidates' in resultado and len(resultado['candidates']) > 0:
                resposta_ia = resultado['candidates'][0]['content']['parts'][0]['text']
                st.markdown(resposta_ia)
                st.session_state.messages.append({"role": "assistant", "content": resposta_ia})
            else:
                msg_erro = resultado.get('error', {}).get('message', 'Erro desconhecido')
                st.error(f"A IA deu erro: {msg_erro}")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")






