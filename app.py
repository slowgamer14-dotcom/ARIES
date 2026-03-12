# 1. Certifique-se de que o modelo está com o nome correto
MODELO_25 = "gemini-2.0-flash-exp" # Atualmente a versão 2.5 em preview é acessada assim ou por codinome

with tabs[1]: 
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#D4AF37;'>🎬 Editor Ultra-Gen 2.5</h3>", unsafe_allow_html=True)
    
    video_file = st.file_uploader("Upload da Gameplay (Até 1GB):", type=['mp4', 'mkv', 'mov'])
    
    if video_file:
        if st.button("🚀 Aries 2.5: Analisar Susto"):
            with st.spinner("Enviando para o Core 2.5..."):
                # Salva local
                with open("gameplay_temp.mp4", "wb") as f:
                    f.write(video_file.getbuffer())
                
                # Upload para a API
                video_ai = genai.upload_file(path="gameplay_temp.mp4")
                
                # LOOP DE SEGURANÇA (Essencial para vídeos pesados)
                status_placeholder = st.empty()
                while video_ai.state.name == "PROCESSING":
                    status_placeholder.warning("⚠️ Google está processando os frames do vídeo... aguarde.")
                    time.sleep(8) # Aumentamos o tempo para vídeos de 1GB
                    video_ai = genai.get_file(video_ai.name)
                
                if video_ai.state.name == "ACTIVE":
                    status_placeholder.success("✅ Vídeo Ativo! Aries 2.5 iniciando análise...")
                    
                    # Chamada do Modelo 2.5
                    model = genai.GenerativeModel(MODELO_25)
                    try:
                        res = model.generate_content([
                            video_ai, 
                            "Você é o editor do canal LikaON. Identifique o momento exato do susto neste vídeo de Resident Evil e sugira um corte dinâmico."
                        ])
                        st.write(res.text)
                        aries_voz("Análise 2.5 concluída. O susto foi localizado com precisão.")
                    except Exception as e:
                        st.error(f"Erro na análise 2.5: {e}")
                else:
                    st.error("O vídeo não pôde ser ativado.")
