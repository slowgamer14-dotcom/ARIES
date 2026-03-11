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
import asyncio
import edge_tts

# 1. Configurações da Página
st.set_page_config(page_title="Aries AI - LikaON Empress", page_icon="♈", layout="wide")

# --- ESTILO VISUAL NEON ---
url_fundo = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/fundo.jpg.png"
url_sidebar = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/sidebar.jpg.png"

st.markdown(f"""
    <style>
    .stApp {{ background-image: url("{url_fundo}"); background-size: cover; background-attachment: fixed; }}
    [data-testid="stSidebar"] {{ background-image: url("{url_sidebar}"); background-size: cover; border-right: 2px solid #ff4b4b; }}
    .stChatMessage {{ background-color: rgba(14, 17, 23, 0.85) !important; border-radius: 15px; border: 1px solid #ff4b4b; margin-bottom: 10px; }}
    div.stButton > button {{ background-color: #ff4b4b; color: white; border-radius: 20px; box-shadow: 0 0 10px #ff4b4b; width: 100%; font-weight: bold; transition: 0.3s; }}
    div.stButton > button:hover {{ transform: scale(1.02); background-color: #ff3333; }}
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Voz (Edge-TTS Grátis)
def aries_fala(texto):
    """Gera áudio neural gratuito da Microsoft"""
    try:
        VOZ = "pt-BR-FranciscaNeural" # Voz sofisticada e natural
        
        async def generate_voice():
            communicate = edge_tts.Communicate(texto, VOZ)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_content = loop.run_until_complete(generate_voice())
        
        audio_b64 = base64.b64encode(audio_content).decode()
        html_audio = f'<audio autoplay style="display:none"><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>'
        st.markdown(html_audio, unsafe_allow_html=True)
    except:
        pass

# 3. Inicialização das APIs
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_DRIVE = st.secrets["GOOGLE_DRIVE_API_KEY"]
    genai.configure(api_key=CHAVE_GEMINI)
except:
    st.error("⚠️ Erro: Chaves API não configuradas nos Secrets!")

MODELO_25 = "gemini-2.5-flash"
INSTRUCAO = "Você é Aries, mentora do canal LikaON. Sofisticada, direta e especialista em mistérios e Resident Evil."

# --- INTERFACE PRINCIPAL ---
st.title("♈ Aries AI - Central LikaON 2.5 Flash")

tab1, tab2 = st.tabs(["💬 Chat Estratégico", "🤖 Edição Autônoma"])

# --- SIDEBAR ---
with st.sidebar:
    st.title("📊 Status")
    st.success("Voz Neural Ativa (Grátis)")
    st.info("Foque no TAF de Bombeiro, eu cuido da edição.")
    st.markdown("---")

# ABA 1: CHAT COM VOZ NEURAL
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
        
        url_api = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO_25}:generateContent?key={CHAVE_GEMINI}"
        payload = {
            "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages],
            "system_instruction": {"parts": [{"text": INSTRUCAO}]}
        }
        
        with st.chat_message("assistant"):
            try:
                res = requests.post(url_api, json=payload).json()
                if "error" in res:
                    st.error(f"Erro Gemini: {res['error']['message']}")
                else:
                    txt = res['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(txt)
                    st.session_state.messages.append({"role": "assistant", "content": txt})
                    aries_fala(txt)
            except Exception as e:
                st.error("Falha na conexão com os servidores da Aries.")

# ABA 2: EDITOR AUTÔNOMO POR ÁUDIO
with tab2:
    st.subheader("📽️ Corte por Transcrição (Gemini 2.5)")
    id_drive = st.text_input("ID do Vídeo no Drive:")
    ordem = st.text_input("O que a Aries deve buscar?", placeholder="Ex: 'Corte o momento do susto'")

    if st.button("🚀 Iniciar Operação de Corte"):
        if id_drive:
            with st.spinner("Aries está ouvindo o áudio da gameplay..."):
                try:
                    # 1. Download do Drive
                    drive_service = googleapiclient.discovery.build('drive', 'v3', developerKey=CHAVE_DRIVE)
                    request = drive_service.files().get_media(fileId=id_drive)
                    with io.FileIO('raw.mp4', 'wb') as fh:
                        downloader = googleapiclient.http.MediaIoBaseDownload(fh, request)
                        done = False
                        while not done: _, done = downloader.next_chunk()

                    # 2. Extrair Áudio
                    video_full = VideoFileClip('raw.mp4')
                    video_full.audio.write_audiofile("raw.mp3")

                    # 3. Análise Multimodal Gemini 2.5
                    sample_file = genai.upload_file(path="raw.mp3")
                    while sample_file.state.name == "PROCESSING":
                        time.sleep(2)
                        sample_file = genai.get_file(sample_file.name)

                    model = genai.GenerativeModel(MODELO_25)
                    prompt_corte = f"Como editora especialista, analise este áudio. Pedido: {ordem}. Retorne JSON: {{'inicio': X, 'fim': Y, 'motivo': '...'}}"
                    response = model.generate_content([sample_file, prompt_corte])
                    genai.delete_file(sample_file.name)
                    
                    decisao = json.loads(response.text.replace("```json", "").replace("```", ""))
                    st.success(f"Aries: {decisao['motivo']}")

                    # 4. Executar Corte e Renderizar
                    clipe = video_full.subclip(decisao['inicio'], decisao['fim'])
                    clipe.write_videofile("final.mp4", codec="libx264", audio_codec="aac", preset="ultrafast")
                    
                    st.video("final.mp4")
                    with open("final.mp4", "rb") as f:
                        st.download_button("📥 Baixar Clipe Editado", f, "likaon_edit.mp4")
                    
                    video_full.close()
                    os.remove('raw.mp4')
                    os.remove('raw.mp3')
                except Exception as e:
                    st.error(f"Erro no processamento: {e}")
      


