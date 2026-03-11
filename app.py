from gtts import gTTS
import base64

# --- FUNÇÃO PARA A ARIES FALAR ---
def aries_fala(texto):
    tts = gTTS(text=texto, lang='pt', tld='com.br')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_b64 = base64.b64encode(fp.read()).decode()
    # Gera um player de áudio que começa sozinho (autoplay)
    html_audio = f'<audio autoplay src="data:audio/mp3;base64,{audio_b64}">'
    st.markdown(html_audio, unsafe_allow_html=True)

# --- ABA 1: CHAT COM VOZ ---
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if p := st.chat_input("Fale com a Aries..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.markdown(p)
        
        # Chamada da API do Gemini (mantendo sua lógica anterior)
        url_api = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={CHAVE_GEMINI}"
        payload = {
            "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages],
            "system_instruction": {"parts": [{"text": INSTRUCAO}]}
        }
        
        with st.chat_message("assistant"):
            try:
                res = requests.post(url_api, json=payload).json()
                txt_resposta = res['candidates'][0]['content']['parts'][0]['text']
                st.markdown(txt_resposta)
                st.session_state.messages.append({"role": "assistant", "content": txt_resposta})
                
                # AQUI A MÁGICA ACONTECE: Ela fala a resposta
                aries_fala(txt_resposta)
                
            except Exception as e:
                st.error("Erro na voz da Aries.")
