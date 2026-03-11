import streamlit as st
import requests

# Configurações da Página
st.set_page_config(page_title="Aries AI", page_icon="♈")

CHAVE_API = "AIzaSyDkKK1i7Cedy1Zdlkn0jhtzOv85DbMeqPA"
MODELO = "gemini-2.5-flash"

# Estilo do Aries (Personalidade)
INSTRUCAO = "Seu nome é Aries. Você é um colaborador autêntico, com um toque de humor e muito prestativo. Ajude o usuário com hardware, YouTube e concursos."

st.title("♈ Aries - Seu Colaborador de IA")

# Inicializa o histórico do chat se não existir
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe as mensagens do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Campo de entrada do usuário
if prompt := st.chat_input("Como posso ajudar hoje?"):
    # Adiciona a pergunta do usuário no chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chamada para o Google
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={CHAVE_API}"
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
            st.error(f"Erro ao conectar: {e}")