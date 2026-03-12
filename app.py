import streamlit as st
import google.generativeai as genai
import time
import os
import re # Para extrair o tempo da resposta
from moviepy.editor import VideoFileClip

# ... (Mantenha suas configurações de interface e API acima) ...

with abas[1]:
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#D4AF37;'>🎬 Central de Edição LikaON</h3>", unsafe_allow_html=True)
    
    video_file = st.file_uploader("Upload da Gameplay (Até 1GB):", type=['mp4', 'mkv', 'mov'])
    
    if video_file:
        st.info(f"📁 Vídeo carregado: {video_file.name}")
        
        if st.button("🚀 Aries 2.5: Cortar Susto"):
            with st.spinner("Analisando e processando o corte..."):
                # 1. Salva o arquivo original
                temp_path = "video_original.mp4"
                with open(temp_path, "wb") as f:
                    f.write(video_file.getbuffer())
                
                try:
                    # 2. IA Analisa o vídeo
                    video_ai = genai.upload_file(path=temp_path)
                    while video_ai.state.name == "PROCESSING":
                        time.sleep(10)
                        video_ai = genai.get_file(video_ai.name)
                    
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    # Prompt rígido para a IA retornar o tempo em formato padrão
                    prompt = "Identifique o susto neste vídeo de Resident Evil. RESPONDA OBRIGATORIAMENTE NO FORMATO 'TEMPO: MM:SS' antes de qualquer descrição."
                    
                    res = model.generate_content([video_ai, prompt])
                    resposta_texto = res.text
                    st.write(resposta_texto)
                    
                    # 3. Extração do Tempo (Regex)
                    match = re.search(r'(\d{1,2}:\d{2})', resposta_texto)
                    
                    if match:
                        tempo_susto = match.group(1)
                        st.success(f"🎯 Susto detectado em: {tempo_susto}")
                        
                        # 4. Corte Físico do Vídeo
                        m, s = map(int, tempo_susto.split(':'))
                        inicio = max(0, (m * 60) + s - 3) # 3 seg antes
                        fim = inicio + 10 # 10 seg de clipe
                        
                        output_path = "susto_pronto_likaon.mp4"
                        
                        with VideoFileClip(temp_path) as video:
                            clipe = video.subclip(inicio, fim)
                            clipe.write_videofile(output_path, codec="libx264", audio_codec="aac")
                        
                        # 5. Botão de Download
                        with open(output_path, "rb") as f:
                            st.download_button(
                                label="📥 BAIXAR VÍDEO PRONTO",
                                data=f,
                                file_name=f"susto_residente_evil_{tempo_susto}.mp4",
                                mime="video/mp4"
                            )
                    else:
                        st.warning("Aries analisou, mas não indicou um tempo exato para o corte.")
                        
                except Exception as e:
                    st.error(f"Erro no processamento: {e}")
                finally:
                    # Limpeza de arquivos temporários
                    if os.path.exists(temp_path): os.remove(temp_path)
                    # O arquivo output_path pode ser removido após o download se desejar
    st.markdown('</div>', unsafe_allow_html=True)
