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

# 1. Configurações de Estilo e Página
st.set_page_config(page_title="Aries AI - LikaON Empress", page_icon="♈", layout="wide")

# [Mantém aqui o teu CSS Neon das versões anteriores]

# 2. Configuração das APIs
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    CHAVE_DRIVE = st.secrets["GOOGLE_DRIVE_API_KEY"]
    genai.configure(api_key=CHAVE_GEMINI)
except:
    st.error("Erro: Chaves de API não encontradas nos Secrets.")

# --- INTERFACE ---
st.title("♈ Aries AI - Editora Autónoma 2.5 Flash")

tab1, tab2 = st.tabs(["💬 Estratégia", "🤖 Edição por Transcrição"])

with tab2:
    st.subheader("🎙️ Modo 'Ouvir e Cortar'")
    st.write("A Aries vai analisar o áudio da tua gameplay e decidir o melhor clipe.")

    id_drive = st.text_input("ID do vídeo no Google Drive:")
    instrucao_ia = st.text_input("O que a Aries deve procurar?", placeholder="Ex: 'Corta o momento em que eu encontro o segredo' ou 'Corta a minha reação de susto'")

    if st.button("🚀 Aries, Assume o Controlo"):
        if id_drive:
            with st.spinner("1. A descarregar e a extrair áudio..."):
                # Download do Drive
                drive_service = googleapiclient.discovery.build('drive', 'v3', developerKey=CHAVE_DRIVE)
                request = drive_service.files().get_media(fileId=id_drive)
                
                video_path = "raw_video.mp4"
                audio_path = "raw_audio.mp3"
                
                with io.FileIO(video_path, 'wb') as fh:
                    downloader = googleapiclient.http.MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        _, done = downloader.next_chunk()

                # Extração do Áudio
                video_full = VideoFileClip(video_path)
                video_full.audio.write_audiofile(audio_path)

            with st.spinner("2. Aries a processar o áudio (IA)..."):
                # Upload do áudio para a File API do Gemini
                sample_file = genai.upload_file(path=audio_path)
                
                # Aguarda o processamento do ficheiro pela Google
                while sample_file.state.name == "PROCESSING":
                    time.sleep(2)
                    sample_file = genai.get_file(sample_file.name)

                # Prompt para a IA decidir o corte
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = (
                    f"Analise este áudio de gameplay. Com base no pedido: '{instrucao_ia}', "
                    "identifique o início e o fim (em segundos) do momento mais relevante. "
                    "Responda estritamente em JSON: {'inicio': X, 'fim': Y, 'motivo': 'explicação'}"
                )
                
                response = model.generate_content([sample_file, prompt])
                
                # Limpa o ficheiro da API da Google após uso
                genai.delete_file(sample_file.name)
                
                try:
                    # Extração do JSON da resposta
                    res_text = response.text.replace("```json", "").replace("```", "").strip()
                    decisao = json.loads(res_text)
                    st.info(f"✨ Aries decidiu: {decisao['motivo']}")
                    st.write(f"⏱️ Corte: {decisao['inicio']}s até {decisao['fim']}s")
                except:
                    st.error("Erro no julgamento da IA. A usar corte padrão.")
                    decisao = {"inicio": 0, "fim": 20}

            with st.spinner("3. A renderizar o teu clipe..."):
                clipe = video_full.subclip(decisao['inicio'], decisao['fim'])
                output_path = "clipe_aries.mp4"
                clipe.write_videofile(output_path, codec="libx264", audio_codec="aac", preset="ultrafast")
                
                st.video(output_path)
                with open(output_path, "rb") as f:
                    st.download_button("📥 Baixar Clipe da Aries", f, "likaon_ai_edit.mp4")
                
                # Limpeza de ficheiros locais
                video_full.close()
                os.remove(video_path)
                os.remove(audio_path)
        else:
            st.warning("Insere o ID do Drive para a Aries poder trabalhar.")


