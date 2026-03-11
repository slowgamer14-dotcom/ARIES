import streamlit as st
import requests
import googleapiclient.discovery
import googleapiclient.http
from moviepy.editor import VideoFileClip
import google.generativeai as genai
import os
import io
import json
import time
import base64
from gtts import gTTS

# 1. Configurações da Página
st.set_page_config(page_title="Aries AI - LikaON Empress", page_icon="♈", layout="wide")

# --- VISUAL NEON ARIES ---
url_fundo = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/fundo.jpg.png"
url_sidebar = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/sidebar.jpg.png"

st.markdown(f"""
    <style>
    .stApp {{ background-image: url("{url_fundo}"); background-size: cover; background-attachment: fixed; }}
    [data-testid="stSidebar"] {{ background-image: url("{url_sidebar}"); background-size: cover; border-right: 2px solid #ff4b4b; }}
    .stChatMessage {{ background-color: rgba(14, 17, 23, 0.85) !important; border-radius: 15px; border: 1px solid #ff4b4b; margin-bottom: 10px; }}
    div.stButton > button {{ background-color: #ff4b4b; color: white; border-radius: 20px; box-shadow: 0 0 10px #ff4b4b; width: 100%; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# 2. Funções Auxiliares
def aries_fala(texto):
    """Gera áudio para a resposta da Aries"""
    try:
        tts = gTTS(text=texto, lang='pt', tld='com.br')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_b64 = base64.b64encode(fp.read()).decode()
        html_audio = f'<audio autoplay src="data:audio/mp3;base64,{audio_b64}">'
        st.markdown(html_audio, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro na geração de voz: {e}")

# 3. Chaves de Segurança
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_DRIVE = st.secrets["GOOGLE_DRIVE_API_KEY"]
    genai.configure(api_key=CHAVE_GEMINI)
except:
    st.error("Erro: Verifique as chaves GEMINI e DRIVE nos Secrets!")

MODELO = "gemini-1.5-flash"
INSTRUCAO = "Você é Aries, mentora do canal LikaON. Sofisticada, direta e focada em gameplay de mistérios e Resident Evil."

# --- ESTRUTURA DE ABAS (CRIAÇÃO DAS VARIÁVEIS) ---
st.title("♈ Aries AI - Sistema de Comando")
tab1, tab2 = st.tabs(["💬 Chat com Voz", "🤖 Editor Autônomo"])

# --- SIDEBAR ---
with st.sidebar:
    st.title("📊 Painel LikaON")
    st.info("Aries agora tem voz! Fale com ela enquanto treina para o TAF.")
    st.markdown("---")

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
                aries_fala(txt_resposta) # Executa a voz
            except:
                st.error("Erro na comunicação com a Aries.")

# --- ABA 2: EDIÇÃO DRIVE ---
with tab2:
    st.subheader("🎙️ Edição por IA de Áudio")
    id_drive = st.text_input("ID do vídeo no Drive:")
    ordem = st.text_input("Comando de edição:")

    if st.button("🚀 Processar"):
        if id_drive:
            with st.spinner("Aries trabalhando..."):
                try:
                    # Download
                    drive_service = googleapiclient.discovery.build('drive', 'v3', developerKey=CHAVE_DRIVE)
                    request = drive_service.files().get_media(fileId=id_drive)
                    with io.FileIO('raw.mp4', 'wb') as fh:
                        downloader = googleapiclient.http.MediaIoBaseDownload(fh, request)
                        done = False
                        while not done: _, done = downloader.next_chunk()

                    # Áudio e IA
                    video_full = VideoFileClip('raw.mp4')
                    video_full.audio.write_audiofile("raw.mp3")
                    
                    sample_file = genai.upload_file(path="raw.mp3")
                    while sample_file.state.name == "PROCESSING": time.sleep(2); sample_file = genai.get_file(sample_file.name)

                    model = genai.GenerativeModel(MODELO)
                    prompt = f"Analise o áudio. Pedido: {ordem}. Retorne JSON: {{'inicio': X, 'fim': Y, 'motivo': '...'}}"
                    response = model.generate_content([sample_file, prompt])
                    genai.delete_file(sample_file.name)
                    
                    decisao = json.loads(response.text.replace("```json", "").replace("```", ""))
                    st.success(f"Aries: {decisao['motivo']}")

                    # Corte
                    clipe = video_full.subclip(decisao['inicio'], decisao['fim'])
                    clipe.write_videofile("final.mp4", codec="libx264", audio_codec="aac", preset="ultrafast")
                    st.video("final.mp4")
                    
                    video_full.close()
                    os.remove('raw.mp4'); os.remove('raw.mp3')
                except Exception as e: st.error(f"Erro: {e}")
