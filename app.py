import streamlit as st
import requests
import googleapiclient.discovery
import googleapiclient.http
from moviepy.editor import VideoFileClip
import os
import io

# 1. Configurações da Página
st.set_page_config(page_title="Aries AI - LikaON Empress", page_icon="♈", layout="wide")

# --- LINKS DAS IMAGENS (RAW) ---
url_fundo = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/fundo.jpg.png"
url_sidebar = "https://raw.githubusercontent.com/slowgamer14-dotcom/ARIES/main/sidebar.jpg.png"

# 2. Visual Neon Aries (CSS)
st.markdown(f"""
    <style>
    .stApp {{ background-image: url("{url_fundo}"); background-size: cover; background-attachment: fixed; }}
    [data-testid="stSidebar"] {{ background-image: url("{url_sidebar}"); background-size: cover; border-right: 2px solid #ff4b4b; }}
    .stChatMessage {{ background-color: rgba(14, 17, 23, 0.85) !important; border-radius: 15px; border: 1px solid #ff4b4b; margin-bottom: 10px; }}
    .stMetric {{ background-color: rgba(30, 37, 46, 0.9); padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; }}
    div.stButton > button {{ background-color: #ff4b4b; color: white; border-radius: 20px; box-shadow: 0 0 10px #ff4b4b; width: 100%; font-weight: bold; transition: 0.3s; }}
    div.stButton > button:hover {{ transform: scale(1.02); background-color: #ff3333; }}
    </style>
    """, unsafe_allow_html=True)

# 3. Chaves de Segurança
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_YOUTUBE = st.secrets["YOUTUBE_API_KEY"]
    CHAVE_DRIVE = st.secrets["GOOGLE_DRIVE_API_KEY"]
except Exception:
    st.error("⚠️ Verifique as chaves GEMINI, YOUTUBE e DRIVE nos Secrets!")

MODELO = "gemini-2.5-flash"
INSTRUCAO = "Seu nome é Aries, mentora do canal LikaON. Você é sofisticada, direta e focada em gameplay e mistérios."

# --- SIDEBAR: ANALYTICS ---
with st.sidebar:
    st.title("📊 Painel LikaON")
    if st.button("🔄 Sincronizar Analytics"):
        try:
            yt = googleapiclient.discovery.build("youtube", "v3", developerKey=CHAVE_YOUTUBE)
            r = yt.channels().list(part="statistics", forHandle="@LikaON3").execute()
            if r.get('items'):
                s = r['items'][0]['statistics']
                st.session_state.inscritos, st.session_state.views = s['subscriberCount'], s['viewCount']
                st.success("Métricas OK!")
            else: st.warning("Canal não encontrado.")
        except: st.error("Erro na API do YouTube.")
    
    if 'inscritos' in st.session_state:
        st.metric("Inscritos", f"{int(st.session_state.inscritos):,}")
        st.metric("Total Views", f"{int(st.session_state.views):,}")
    
    st.markdown("---")
    st.caption("Aries v2.5 Flash | Edição Cloud")

# --- CONTEÚDO PRINCIPAL ---
st.title("♈ Aries AI - Central de Comando")
tab1, tab2 = st.tabs(["💬 Chat Estratégico", "☁️ Editor Google Drive"])

# ABA 1: CHAT
with tab1:
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("Fale com a Aries..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        # Linha 78 Corrigida aqui:
        url_api = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={CHAVE_GEMINI}"
        payload = {
            "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages],
            "system_instruction": {"parts": [{"text": INSTRUCAO}]}
        }
        with st.chat_message("assistant"):
            try:
                res = requests.post(url_api, json=payload).json()
                txt = res['candidates'][0]['content']['parts'][0]['text']
                st.markdown(txt)
                st.session_state.messages.append({"role": "assistant", "content": txt})
            except: st.error("Erro ao conectar com a Aries.")

# ABA 2: EDITOR DRIVE
with tab2:
    st.subheader("🎞️ Editor LikaON Cloud")
    file_id = st.text_input("ID do vídeo no Drive:")
    
    col1, col2 = st.columns(2)
    s_t = col1.number_input("Início (seg)", min_value=0, value=0)
    e_t = col2.number_input("Fim (seg)", min_value=1, value=10)

    if st.button("🚀 Processar Corte"):
        if file_id:
            with st.spinner("Aries está operando..."):
                try:
                    drive_service = googleapiclient.discovery.build('drive', 'v3', developerKey=CHAVE_DRIVE)
                    request = drive_service.files().get_media(fileId=file_id)
                    with io.FileIO('temp.mp4', 'wb') as fh:
                        downloader = googleapiclient.http.MediaIoBaseDownload(fh, request)
                        done = False
                        while not done:
                            status, done = downloader.next_chunk()
                    
                    with VideoFileClip('temp.mp4') as video:
                        clipe = video.subclip(s_t, e_t)
                        clipe.write_videofile("final.mp4", codec="libx264", audio_codec="aac", fps=24, preset="ultrafast")
                    
                    st.video("final.mp4")
                    with open("final.mp4", "rb") as f:
                        st.download_button("📥 Baixar Vídeo", f, "gameplay_likaon.mp4")
                    os.remove('temp.mp4')
                except Exception as e: st.error(f"Erro: {e}")
        else: st.warning("Insira o ID do arquivo.")

