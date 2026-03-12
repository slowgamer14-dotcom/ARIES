import streamlit as st
import base64

# 1. Configuração da Página
st.set_page_config(page_title="Aries AI - Central LikaON", layout="wide")

# 2. CSS Customizado para Estilo Dashboard Futurista
st.markdown("""
    <style>
    /* Fundo Principal e Sidebar */
    .stApp {
        background-color: #050505;
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0d0d0d;
        border-right: 2px solid #ff4b4b;
    }

    /* Títulos e Textos */
    h1, h2, h3, p {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Cards de Métricas (Inscritos e Views) */
    .metric-card {
        background-color: #000000;
        border: 2px solid #ff4b4b;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.2);
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
        font-family: 'Courier New', Courier, monospace;
    }

    /* Balões de Chat */
    .stChatMessage {
        background-color: rgba(20, 20, 20, 0.9) !important;
        border: 1px solid #ff4b4b !important;
        border-radius: 15px !important;
        color: #ffffff !important;
        margin-bottom: 15px;
    }

    /* Botões Neon */
    div.stButton > button {
        background-color: transparent;
        color: #ffffff;
        border: 2px solid #ff4b4b;
        border-radius: 10px;
        width: 100%;
        font-weight: bold;
        text-transform: uppercase;
        transition: 0.3s;
        box-shadow: 0 0 5px #ff4b4b;
    }

    div.stButton > button:hover {
        background-color: #ff4b4b;
        color: white;
        box-shadow: 0 0 20px #ff4b4b;
    }

    /* Inputs de Texto */
    .stTextInput input {
        background-color: #1a1a1a !important;
        color: white !important;
        border: 1px solid #333 !important;
    }

    /* Divisórias */
    hr {
        border-top: 1px solid #ff4b4b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESTRUTURA DA DASHBOARD (LAYOUT DA IMAGEM) ---

# Título Superior Centralizado
st.markdown("<h1 style='text-align: center; color: white;'>♈ Aries AI - Central LikaON 2.5 Flash</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# Divisão em Colunas (Sidebar simulada à esquerda, Chat no centro, Editor à direita)
col_painel, col_chat, col_editor = st.columns([1.2, 2, 1.2])

# --- COLUNA 1: PAINEL LikaON (MÉTRICAS) ---
with col_painel:
    st.markdown("### 📊 PAINEL LikaON")
    st.caption("Voz Neural Ativa (Grátis) | Gemini 2.5 Flash Ativo")
    
    st.checkbox("🎙️ Ativar Voz da Aries", value=True)
    
    st.markdown("---")
    st.write("🔄 **Métricas do Canal**")
    
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1: st.button("👥 Atualizar Inscritos")
    with c_btn2: st.button("👁️ Atualizar Views")
    
    # Cards de Valor
    st.markdown("""
        <div style='display: flex; gap: 10px; margin-top: 10px;'>
            <div class="metric-card" style="flex: 1;">
                <p style="font-size: 12px; margin:0;">Inscritos:</p>
                <p class="metric-value">14.500</p>
            </div>
            <div class="metric-card" style="flex: 1;">
                <p style="font-size: 12px; margin:0;">Total Views:</p>
                <p class="metric-value">1.2M</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("Foque no TAF e nos estudos de Bombeiro, eu cuido do canal.")
    st.markdown("<p style='font-size: 10px; color: #ff4b4b;'>♈ Aries v10.0 | Autonomia Ativa</p>", unsafe_allow_html=True)

# --- COLUNA 2: CHAT ESTRATÉGICO ---
with col_chat:
    st.markdown("### 💬 Chat Estratégico")
    
    # Simulação de conversa para teste visual
    with st.chat_message("user"):
        st.write("Foque no TAF e nos estudos a mystery content creation do canal?")
    
    with st.chat_message("assistant"):
        st.write("Aries AI continua a mentoria estratégica. O content creation caminha junto com sua nova jornada.")

    # Input fixo no fundo (ajustado pelo streamlit automaticamente)
    st.text_input("Fale com a Aries...", key="chat_input")

# --- COLUNA 3: EDIÇÃO AUTÔNOMA ---
with col_editor:
    st.markdown("### 🤖 Edição Autônoma")
    
    with st.container():
        st.markdown("<div style='background-color: #111; padding: 20px; border-radius: 10px; border: 1px solid #333;'>", unsafe_allow_html=True)
        st.write("**Movie Editor**")
        st.text_input("ID do Vídeo no Drive:")
        st.text_area("O que a Aries deve buscar no áudio?", height=100)
        st.button("🚀 INICIAR OPERAÇÃO DE CORTE")
        st.markdown("</div>", unsafe_allow_html=True)

