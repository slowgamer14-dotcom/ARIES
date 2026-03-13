import streamlit as st
import moviepy.editor as mp
import numpy as np
import os

# Configuração da Página
st.set_page_config(page_title="Editor IA de Gameplay", page_icon="🎮")

st.title("🎮 IA Editor Pro: Gameplay Edition")
st.markdown("Transforme sua live em um vídeo editado de 15-20 min automaticamente.")

# Sidebar para configurações
st.sidebar.header("⚙️ Ajustes da IA")
sensibilidade = st.sidebar.slider("Sensibilidade de Áudio (Corte)", 0.01, 0.10, 0.02)
padding = st.sidebar.slider("Margem de segurança (segundos)", 1, 5, 2)

# Upload de Arquivos
video_file = st.file_uploader("Suba sua Live (.mp4)", type=["mp4"])

if video_file:
    # Salvar arquivo temporário
    with open("input_video.mp4", "wb") as f:
        f.write(video_file.getbuffer())

    if st.button("🚀 Iniciar Edição Mágica"):
        with st.status("Processando vídeo... isso pode demorar dependendo do tamanho da live.") as status:
            
            video = mp.VideoFileClip("input_video.mp4")
            
            # IA de detecção de som
            st.write("🔍 Analisando onde a ação acontece...")
            # Encontra intervalos onde o volume está acima do limite
            intervals = video.audio.nls_intervals(threshold=sensibilidade)
            
            # Adiciona uma margem de segurança nos cortes para não ficar brusco
            final_clips = []
            for start, end in intervals:
                start = max(0, start - padding)
                end = min(video.duration, end + padding)
                final_clips.append(video.subclip(start, end))
            
            if final_clips:
                st.write(f"✂️ Juntando {len(final_clips)} melhores momentos...")
                final_video = mp.concatenate_videoclips(final_clips, method="compose")
                
                output_filename = "video_editado_final.mp4"
                final_video.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=24)
                
                status.update(label="✅ Edição Concluída!", state="complete")
                
                with open(output_filename, "rb") as f:
                    st.download_button("📥 Baixar Vídeo para YouTube", f, file_name="gameplay_editada.mp4")
            else:
                st.error("Nenhum momento de som detectado. Tente baixar a sensibilidade.")
