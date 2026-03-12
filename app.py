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
    .stMetric {{ background-color: rgba(0,0,0,0.6); padding: 10px; border-radius: 10px; border: 1px solid #ff4b4b; }}
    
    /* Estilização do Checkbox para combinar com o layout */
    div[data-testid="stCheckbox"] {{
        background-color: rgba(61, 10, 10, 0.5);
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #ff4b4b;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Voz (Edge-TTS Grátis)
def aries_fala(texto):
    # Verifica se a voz está ativa no session_state
    if not st.session_state.get("permitir_voz", True):
        return
    try:
        VOZ = "pt-BR-FranciscaNeural"
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
        st.markdown(f'<audio autoplay style="display:none"><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: 
        pass

# 3. Inicialização e APIs
if "messages" not in st.session_state: st.session_state.messages = []
if "inscritos" not in st.session_state: st.session_state.inscritos = 0
if "views" not in st.session_state: st.session_state.views = 0

try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_DRIVE = st.secrets["GOOGLE_DRIVE_API_KEY"]
    CHAVE_YOUTUBE = st.secrets["YOUTUBE_API_KEY"]
    genai.configure(api_key=CHAVE_GEMINI)
except:
    st.error("⚠️ Erro: Chaves API não configuradas nos Secrets!")

MODELO_25 = "gemini-2.5-flash"
INSTRUCAO = "Você é Aries, mentora do canal LikaON. Sofisticada, direta e especialista em mistérios e Resident Evil."

# --- SIDEBAR (MÉTRICAS E CONTROLE) ---
with st.sidebar:
    st.title("📊 Painel LikaON")
    
    # BOTÃO DE VOZ (O que você pediu)
    st.session_state.permitir_voz = st.checkbox("🎙️ Ativar Voz da Aries", value=True)
    
    st.markdown("---")
    
    def buscar_stats():
        try:
            yt = googleapiclient.discovery.build("youtube", "v3", developerKey=CHAVE_YOUTUBE)
            r = yt.channels().list(part="statistics", forHandle="@LikaON3").execute()
            return r['items'][0]['statistics'] if r.get('items') else None
        except: 
            return None

    st.subheader("Métricas em Tempo Real")
    if st.button("👥 Atualizar Inscritos"):
        s = buscar_stats()
        if s: st.session_state.inscritos = s['subscriberCount']
    
    if st.button("👁️ Atualizar Views"):
        s = buscar_stats()
        if s: st.session_state.views = s['viewCount']

    st.markdown("---")
    c1, c2 = st.columns(2)
    c1.metric("Inscritos", f"{int(st.session_state.inscritos):,}".replace(",", "."))
    c2.metric("Views", f"{int(st.session_state.views):,}".replace(",", "."))
    st.markdown("---")
    st.info("Foque no TAF e no concurso, eu cuido do resto.")

# --- INTERFACE PRINCIPAL ---
st.title("♈ Aries AI - Central LikaON")
tab1, tab2 = st.tabs(["💬 Chat Estratégico", "🤖 Editor Autônomo"])

# ABA 1: CHAT
with tab1:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): 
            st.markdown(m["content"])

    if p := st.chat_input("Fale com a Aries..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): 
            st.markdown(p)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO_25}:generateContent?key={CHAVE_GEMINI}"
        payload = {
            "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages],
            "system_instruction": {"parts": [{"text": INSTRUCAO}]}
        }
        
        with st.chat_message("assistant"):
            try:
                res = requests.post(url, json=payload).json()
                txt = res['candidates'][0]['content']['parts'][0]['text']
                st.markdown(txt)
                st.session_state.messages.append({"role": "assistant", "content": txt})
                aries_fala(txt)
            except: 
                st.error("Erro na conexão.")

# ABA 2: EDITOR
with tab2:
    st.subheader("📽️ Corte Inteligente (Gemini 2.5)")
    id_drive = st.text_input("ID do Vídeo no Drive:")
    ordem = st.text_input("O que devo buscar no áudio?")
    
    if st.button("🚀 Iniciar Operação"):
        if id_drive:
            with st.spinner("Analisando áudio..."):
                try:
                    drive = googleapiclient.discovery.build('drive', 'v3', developerKey=CHAVE_DRIVE)
                    req = drive.files().get_media(fileId=id_drive)
                    
                    with io.FileIO('raw.mp4', 'wb') as f:
                        down = googleapiclient.http.MediaIoBaseDownload(f, req)
                        done = False
                        while not done: 
                            _, done = down.next_chunk()
                    
                    v = VideoFileClip('raw.mp4')
                    v.audio.write_audiofile("raw.mp3")
                    
                    sf = genai.upload_file(path="raw.mp3")
                    while sf.state.name == "PROCESSING": 
                        time.sleep(2)
                        sf = genai.get_file(sf.name)
                    
                    m = genai.GenerativeModel(MODELO_25)
                    res = m.generate_content([sf, f"Pedido: {ordem}. Retorne JSON {{'inicio': X, 'fim': Y, 'motivo': '...'}}"])
                    genai.delete_file(sf.name)
                    
                    # Limpeza para garantir JSON puro
                    clean_res = res.text.replace("```json", "").replace("```", "").strip()
                    d = json.loads(clean_res)
                    
                    st.success(f"Aries: {d['motivo']}")
                    clipe = v.subclip(d['inicio'], d['fim'])
                    clipe.write_videofile("final.mp4", codec="libx264", audio_codec="aac", preset="ultrafast")
                    
                    st.video("final.mp4")
                    v.close()
                    os.remove('raw.mp4')
                    os.remove('raw.mp3')
                except Exception as e: 
                    st.error(f"Erro: {e}")

