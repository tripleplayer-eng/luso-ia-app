import streamlit as st
import google.generativeai as genai
import pandas as pd
import time
import random
from datetime import datetime
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx
from google.api_core import exceptions

# --- CONFIGURAÇÃO (LAYOUT LARGO PARA NÃO ESMAGAR) ---
st.set_page_config(
    page_title="Luso-IA", 
    page_icon="🇵🇹", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- CSS DE LIMPEZA (REMOVER RODAPÉ) ---
st.markdown("""
    <style>
        /* Fundo Preto */
        .stApp { background-color: #000000; }
        
        /* Remover TUDO o que é rodapé e menu */
        header {visibility: hidden;}
        footer {visibility: hidden; display: none;}
        #MainMenu {visibility: hidden; display: none;}
        .stDeployButton {display: none;}
        [data-testid="stDecoration"] {display: none;}
        div[data-testid="stStatusWidget"] {display: none;}
        
        /* Inputs Legíveis */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 2px solid #555 !important;
            border-radius: 8px !important;
        }
        
        /* Texto Branco */
        h1, h2, h3, p, label, div, span { color: #e2e8f0 !important; }
        
        /* Botões de Rede (Estilo Botão Normal) */
        .stButton button {
            width: 100%;
            border-radius: 8px;
            font-weight: bold;
            background-color: #1f2937;
            color: white;
            border: 1px solid #374151;
            transition: 0.2s;
        }
        .stButton button:hover {
            border-color: #3b82f6;
            color: #3b82f6;
        }
        /* Botão selecionado (Simulação) */
        .stButton button:active {
            background-color: #3b82f6;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# --- LINKS ---
LINK_DA_BASE_DE_DADOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_xyKHdsk9og2mRKE5uZBKcANNFtvx8wuUhR3a7gV-TFlZeSuU2wzJB_SjfkUKKIqVhh3LcaRr8Wn3/pub?gid=0&single=true&output=csv"
LINK_TALLY = "https://tally.so/r/81qLVx"

# --- MOTOR DE IA "OLD RELIABLE" ---
def gerar_conteudo_final(prompt):
    keys = []
    if "GOOGLE_KEYS" in st.secrets: keys = st.secrets["GOOGLE_KEYS"]
    elif "GOOGLE_API_KEY" in st.secrets: keys = [st.secrets["GOOGLE_API_KEY"]]
    
    if not keys: return None, "Chave API não configurada."
    random.shuffle(keys)
    
    # USAR APENAS GEMINI-PRO (UNIVERSAL)
    for key in keys:
        try:
            genai.configure(api_key=key)
            model_ai = genai.GenerativeModel("gemini-pro")
            response = model_ai.generate_content(prompt)
            return response, None
        except Exception as e:
            continue
            
    return None, "Erro de conexão. Tente novamente."

# --- RASTREAMENTO IP ---
@st.cache_resource
def get_usage_tracker(): return {}

def get_remote_ip():
    try:
        ctx = get_script_run_ctx()
        if ctx is None: return "unknown"
        session_info = runtime.get_instance().get_client(ctx.session_id)
        if session_info is None: return "unknown"
        return session_info.request.remote_ip
    except:
        if "session_id" not in st.session_state: st.session_state.session_id = random.randint(1, 1000000)
        return f"session_{st.session_state.session_id}"

usage_tracker = get_usage_tracker()
user_ip = get_remote_ip()

@st.cache_data(ttl=60)
def carregar_clientes():
    try:
        df = pd.read_csv(LINK_DA_BASE_DE_DADOS)
        df.columns = df.columns.str.strip()
        if 'Email' in df.columns and 'Senha' in df.columns:
            df['Email'] = df['Email'].astype(str).str.strip()
            df['Senha'] = df['Senha'].astype(str).str.strip()
            return dict(zip(df.Email, df.Senha))
        return {}
    except: return {}

# --- GESTÃO DE ESTADO (Para os botões) ---
if "rede_selecionada" not in st.session_state:
    st.session_state.rede_selecionada = "Instagram"

def set_rede(nome):
    st.session_state.rede_selecionada = nome

# --- LOGIN ---
def check_login():
    if "user_type" not in st.session_state: st.session_state.user_type = None
    if st.session_state.user_type: return True

    try: st.image("logo.png", width=150) 
    except: pass
    
    st.markdown("### 🔒 Login Luso-IA")
    tab1, tab2 = st.tabs(["🔑 Entrar", "🎁 Testar"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email:")
            senha = st.text_input("Senha:", type="password")
            if st.form_submit_button("Entrar"):
                try:
                    if st.secrets["clientes"]["admin"] == senha:
                        st.session_state.user_type = "PRO"
                        st.session_state.user_email = "Admin"
                        st.success("Admin Ativo")
                        time.sleep(0.5)
                        st.rerun()
                except: pass
                clientes = carregar_clientes()
                if email in clientes and clientes[email] == senha:
                    st.session_state.user_type = "PRO"
                    st.session_state.user_email = email
                    st.rerun()
                else: st.error("Dados incorretos.")
    
    with tab2:
        usos_atuais = usage_tracker.get(user_ip, 0)
        if usos_atuais >= 3:
             st.error("🚫 Demonstrações esgotadas.")
             st.markdown(f"<a href='{LINK_TALLY}' target='_blank' style='display:block;text-align:center;background:#dc2626;color:white;padding:12px;border-radius:8px;text-decoration:none;font-weight:bold;'>Ativar Acesso</a>", unsafe_allow_html=True)
        else:
            restantes = 3 - usos_atuais
            st.info(f"Tem {restantes} gerações gratuitas.")
            if st.button("Começar Demo"):
                st.session_state.user_type = "DEMO"
                st.rerun()
    return False

# --- APP ---
if check_login():
    # Header simples
    try: st.image("logo.png", width=120)
    except: st.write("🌍 Luso-IA")
    
    if st.session_state.user_type != "PRO":
        usos_ip = usage_tracker.get(user_ip, 0)
        restantes = 3 - usos_ip
        if restantes <= 0:
            st.error("Demonstração terminada.")
            st.markdown(f"<a href='{LINK_TALLY}' target='_blank' style='display:block;text-align:center;background:#dc2626;color:white;padding:15px;border-radius:8px;text-decoration:none;font-size:1.1em;'>🔓 Desbloquear</a>", unsafe_allow_html=True)
            st.stop()
        else:
            st.caption(f"⚠️ Modo Demo: {restantes} restantes")

    # --- SELETOR DE REDES (BOTÕES REAIS) ---
    st.write("### 📢 Escolha a Plataforma")
    
    # Grelha de botões manuais (Indestrutível)
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        if st.button("📸 Insta", use_container_width=True): set_rede("Instagram")
    with c2: 
        if st.button("💼 Linked", use_container_width=True): set_rede("LinkedIn")
    with c3: 
        if st.button("🎵 TikTok", use_container_width=True): set_rede("TikTok")
    with c4: 
        if st.button("📘 Face", use_container_width=True): set_rede("Facebook")
        
    c5, c6, c7, c8 = st.columns(4)
    with c5: 
        if st.button("▶️ Tube", use_container_width=True): set_rede("YouTube")
    with c6: 
        if st.button("🐦 Twitter", use_container_width=True): set_rede("Twitter")
    with c7: 
        if st.button("💬 Whats", use_container_width=True): set_rede("WhatsApp")
    with c8: 
        if st.button("📝 Blog", use_container_width=True): set_rede("Blog")

    # Mostra o que está selecionado
    st.info(f"✅ Rede Selecionada: **{st.session_state.rede_selecionada}**")

    # --- FORMULÁRIO ---
    st.markdown("---")
    with st.form("gerador"):
        c_pais, c_tom = st.columns(2)
        with c_pais: 
            pais = st.selectbox("País", ["🇵🇹 Portugal", "🇧🇷 Brasil", "🇦🇴 Angola", "🇲🇿 Moçambique", "🇨🇻 Cabo Verde", "🇬🇼 Guiné", "🇸🇹 São Tomé", "🇹🇱 Timor"])
        with c_tom: 
            tom = st.selectbox("Tom", ["Profissional", "Divertido", "Vendas", "Storytelling", "Urgente"])
            
        negocio = st.text_input("Negócio:", placeholder="Ex: Café Central")
        tema = st.text_area("Tópico:", placeholder="Ex: Promoção de pequeno-almoço")
        
        # Botão de Gerar Grande e Colorido
        st.markdown("""<style>div[data-testid="stFormSubmitButton"] button {background: #f59e0b !important; color: black !important; border: none;}</style>""", unsafe_allow_html=True)
        btn = st.form_submit_button("✨ CRIAR CONTEÚDO AGORA")

    if btn and negocio:
        if st.session_state.user_type == "DEMO":
            current_usage = usage_tracker.get(user_ip, 0)
            if current_usage < 3:
                usage_tracker[user_ip] = current_usage + 1
                if usage_tracker[user_ip] >= 3: time.sleep(1)
            else: st.rerun()

        # GERAÇÃO
        with st.spinner("A criar magia..."):
            prompt = f"""
            Atua como Copywriter Sénior. 
            País: {pais}. Rede: {st.session_state.rede_selecionada}. Tom: {tom}. 
            Negócio: {negocio}. Tópico: {tema}. 
            """
            
            response, erro = gerar_conteudo_final(prompt)
            if response:
                st.markdown("### 📝 O seu texto:")
                st.markdown(response.text)
                st.markdown("---")
            else:
                st.error(f"⚠️ Erro IA: {erro}")

            # IMAGEM (POLLINATIONS SIMPLES)
            try:
                clean_keywords = f"{negocio} {tema} {pais}"
                clean_keywords = urllib.parse.quote(clean_keywords)
                url_img = f"https://image.pollinations.ai/prompt/professional%20photo%20of%20{clean_keywords}?width=1024&height=1024&model=flux&nologo=true"
                st.image(url_img, caption="Sugestão Visual")
            except: pass

    st.markdown("<br><br>", unsafe_allow_html=True)
