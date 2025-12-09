import streamlit as st
import google.generativeai as genai
import pandas as pd
from streamlit_image_select import image_select
import time
import random
import urllib.parse
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx

# --- CONFIGURAÇÃO ---
st.set_page_config(
    page_title="Luso-IA", 
    page_icon="🇵🇹", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS NUCLEAR ---
st.markdown("""
    <style>
        header[data-testid="stHeader"] {visibility: hidden; height: 0px;}
        #MainMenu {visibility: hidden; display: none;}
        footer {visibility: hidden; display: none;}
        .block-container {padding-top: 1rem !important; padding-bottom: 5rem !important;}
        .stButton button { 
            width: 100%; border-radius: 12px; font-weight: 600; 
            background: linear-gradient(90deg, #2563eb, #4f46e5); color: white; border: none; padding: 0.8rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stButton button:hover { transform: scale(1.02); box-shadow: 0 6px 12px rgba(0,0,0,0.15); }
    </style>
""", unsafe_allow_html=True)

# --- LINKS ---
LINK_DA_BASE_DE_DADOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_xyKHdsk9og2mRKE5uZBKcANNFtvx8wuUhR3a7gV-TFlZeSuU2wzJB_SjfkUKKIqVhh3LcaRr8Wn3/pub?gid=0&single=true&output=csv"
LINK_TALLY = "https://tally.so/r/81qLVx"

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

# --- CARREGAR CLIENTES ---
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

# --- LOGIN ---
def check_login():
    if "user_type" not in st.session_state: st.session_state.user_type = None
    if st.session_state.user_type: return True

    try: st.image("logo.png", width=200) 
    except: pass
    
    st.markdown("### 🔒 Login Luso-IA")
    
    tab1, tab2 = st.tabs(["🔑 Entrar", "🎁 Testar"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email:")
            senha = st.text_input("Senha:", type="password")
            if st.form_submit_button("Entrar"):
                if senha == "SOU-O-DONO":
                    st.session_state.user_type = "PRO"
                    st.session_state.user_email = "Admin"
                    st.rerun()
                clientes = carregar_clientes()
                if email in clientes and clientes[email] == senha:
                    st.session_state.user_type = "PRO"
                    st.session_state.user_email = email
                    st.rerun()
                else: st.error("Dados incorretos.")
    
    with tab2:
        usos_atuais = usage_tracker.get(user_ip, 0)
        if usos_atuais >= 3:
             st.error("🚫 Já utilizou as suas 3 demonstrações gratuitas.")
             st.markdown(f"<a href='{LINK_TALLY}' target='_blank' style='display:block;text-align:center;background:#dc2626;color:white;padding:12px;border-radius:8px;text-decoration:none;font-weight:bold;'>Ativar Acesso Ilimitado</a>", unsafe_allow_html=True)
        else:
            restantes = 3 - usos_atuais
            st.info(f"Tem direito a {restantes} gerações neste dispositivo.")
            if st.button("Começar Demo"):
                st.session_state.user_type = "DEMO"
                st.rerun()
    return False

# --- MOTOR ---
def get_working_model():
    try:
        lista = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        preferidos = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        for m in preferidos:
            if m in lista: return m
        return lista[0] if lista else "gemini-pro"
    except: return "gemini-pro"

# --- APP ---
if check_login():
    col1, col2 = st.columns([1, 4])
    with col1:
        try: st.image("logo.png", width=100)
        except: st.write("🌍")
    with col2:
        st.title("Luso-IA")
        if st.session_state.user_type == "PRO": st.success("✅ Modo PRO Ativo")
        else:
            usos_ip = usage_tracker.get(user_ip, 0)
            restantes = 3 - usos_ip
            if restantes <= 0:
                st.error("Demonstração terminada.")
                st.markdown(f"<a href='{LINK_TALLY}' target='_blank' style='display:block;text-align:center;background:#dc2626;color:white;padding:15px;border-radius:8px;text-decoration:none;font-size:1.1em;'>🔓 Desbloquear Acesso Ilimitado</a>", unsafe_allow_html=True)
                st.stop()
            else: st.warning(f"⚠️ Demo: {restantes} restantes")

    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        modelo_ativo = get_working_model()
    except:
        st.error("Erro API Key.")
        st.stop()

    st.write("### Publicar onde?")
    
    # LISTA COMPLETA DE ÍCONES (TikTok, Blog, Twitter incluídos)
    rede_selecionada = image_select(
        label="",
        images=[
            "https://cdn-icons-png.flaticon.com/512/2111/2111463.png", # Instagram
            "https://cdn-icons-png.flaticon.com/512/174/174857.png",   # LinkedIn
            "https://cdn-icons-png.flaticon.com/512/5968/5968764.png", # Facebook
            "https://cdn-icons-png.flaticon.com/512/3046/3046121.png", # TikTok
            "https://cdn-icons-png.flaticon.com/512/1384/1384060.png", # YouTube
            "https://cdn-icons-png.flaticon.com/512/5969/5969020.png", # X / Twitter
            "https://cdn-icons-png.flaticon.com/512/4922/4922073.png", # Blog
            "https://cdn-icons-png.flaticon.com/512/733/733585.png"    # WhatsApp
        ],
        captions=["Instagram", "LinkedIn", "Facebook", "TikTok", "YouTube", "X (Twitter)", "Blog Post", "WhatsApp"],
        index=0, use_container_width=False
    )

    with st.form("gerador"):
        col_a, col_b = st.columns(2)
        with col_a: pais = st.selectbox("País", ["🇵🇹 Portugal", "🇧🇷 Brasil", "🇦🇴 Angola", "🇲🇿 Moçambique", "🇨🇻 Cabo Verde", "🇬🇼 Guiné", "🇸🇹 São Tomé", "🇹🇱 Timor"])
        with col_b: tom = st.selectbox("Tom", ["Profissional", "Vendas", "Storytelling"])
        negocio = st.text_input("Negócio:", placeholder="Ex: Café Central")
        tema = st.text_area("Tópico:", placeholder="Ex: Promoção de pequeno-almoço")
        btn = st.form_submit_button("✨ Criar Conteúdo")

    if btn and negocio:
        if st.session_state.user_type == "DEMO":
            current_usage = usage_tracker.get(user_ip, 0)
            if current_usage < 3:
                usage_tracker[user_ip] = current_usage + 1
                if usage_tracker[user_ip] >= 3: time.sleep(1)
            else: st.rerun()

        # Lógica de seleção corrigida para os novos ícones
        rede_nome = "Rede Social"
        if "2111463" in rede_selecionada: rede_nome = "Instagram"
        elif "174857" in rede_selecionada: rede_nome = "LinkedIn"
        elif "5968764" in rede_selecionada: rede_nome = "Facebook"
        elif "3046121" in rede_selecionada: rede_nome = "TikTok"
        elif "1384060" in rede_selecionada: rede_nome = "YouTube Shorts"
        elif "5969020" in rede_selecionada: rede_nome = "X (Twitter)"
        elif "4922073" in rede_selecionada: rede_nome = "Artigo de Blog"
        elif "733585" in rede_selecionada: rede_nome = "WhatsApp"

        with st.spinner("A escrever..."):
            prompt = f"Copywriter Expert. País: {pais}. Rede: {rede_nome}. Tom: {tom}. Negócio: {negocio}. Tópico: {tema}. Cria texto focado em vendas e cultura local."
            try:
                model = genai.GenerativeModel(modelo_ativo)
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e: st.error(f"Erro Texto: {e}")

        with st.spinner("A gerar fotografia realista..."):
            try:
                seed = random.randint(1, 999999)
                prompt_img = f"Photorealistic photo of {tema} inside a {negocio}, {pais} style context, natural lighting, high resolution, 4k, cinematic, highly detailed, no text, no watermark"
                prompt_clean = urllib.parse.quote(prompt_img)
                url_img = f"https://image.pollinations.ai/prompt/{prompt_clean}?width=1024&height=1024&model=flux&seed={seed}&nologo=true"
                st.image(url_img)
                st.caption("⚠️ **Nota:** Imagem gerada por IA meramente ilustrativa. Pode usar livremente se julgar conveniente.")
            except: st.warning("Imagem indisponível.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; color: #ccc; font-size: 0.8rem;'>Luso-IA • {pais.split(' ')[1]}</div>", unsafe_allow_html=True)
