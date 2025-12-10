import streamlit as st
import google.generativeai as genai
import pandas as pd
from streamlit_image_select import image_select
import time
import random
import urllib.parse
from datetime import datetime
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx
from google.api_core import exceptions

# --- CONFIGURAÇÃO ---
st.set_page_config(
    page_title="Luso-IA", 
    page_icon="🇵🇹", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS ESTILO iOS (CENTRADO E LIMPO) ---
st.markdown("""
    <style>
        /* 1. Fundo Escuro */
        .stApp { background-color: #000000; }
        
        /* 2. Centralizar os Ícones (O Segredo) */
        iframe {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        
        /* 3. Inputs Modernos (Cinza Apple) */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
            background-color: #1c1c1e !important; /* Cinza iOS */
            color: white !important;
            border: 1px solid #3a3a3c !important;
            border-radius: 12px !important;
        }
        
        /* 4. Botão Gerar (Azul Apple) */
        .stButton button { 
            width: 100%; border-radius: 14px; font-weight: 600; font-size: 18px;
            background-color: #007AFF !important; color: white !important; border: none; padding: 12px;
        }
        
        /* 5. Limpeza */
        header[data-testid="stHeader"] {visibility: hidden; height: 0px;}
        #MainMenu, footer {display: none;}
        .block-container {padding-top: 2rem !important; padding-bottom: 5rem !important;}
        h3 { text-align: center; font-weight: 300; color: #a1a1aa !important; font-size: 16px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- LINKS ---
LINK_DA_BASE_DE_DADOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_xyKHdsk9og2mRKE5uZBKcANNFtvx8wuUhR3a7gV-TFlZeSuU2wzJB_SjfkUKKIqVhh3LcaRr8Wn3/pub?gid=0&single=true&output=csv"
LINK_TALLY = "https://tally.so/r/81qLVx"

# --- MOTOR DE IA (UNIVERSAL) ---
def gerar_conteudo_final(prompt):
    keys = []
    if "GOOGLE_KEYS" in st.secrets: keys = st.secrets["GOOGLE_KEYS"]
    elif "GOOGLE_API_KEY" in st.secrets: keys = [st.secrets["GOOGLE_API_KEY"]]
    
    if not keys: return None, "Sem chaves API."
    random.shuffle(keys)
    
    # Se atualizaste o requirements.txt, o 'gemini-1.5-flash' vai funcionar
    # Se não, ele cai para o 'gemini-pro'
    modelos = ["gemini-1.5-flash", "gemini-pro"]
    
    for modelo in modelos:
        for key in keys:
            try:
                genai.configure(api_key=key)
                model_ai = genai.GenerativeModel(modelo)
                response = model_ai.generate_content(prompt)
                return response, None
            except Exception as e:
                if "404" in str(e): break # Modelo não existe, tenta o próximo
                continue # Quota cheia, tenta outra chave
                
    return None, "Erro de conexão. Tente novamente em 10s."

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

def get_current_date():
    meses = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}
    h = datetime.now()
    return f"{h.day} de {meses[h.month]} de {h.year}"

# --- LOGIN ---
def check_login():
    if "user_type" not in st.session_state: st.session_state.user_type = None
    if st.session_state.user_type: return True

    try: st.image("logo.png", width=150) 
    except: pass
    
    st.markdown("<h3 style='color:white !important; font-size:20px;'>Bem-vindo à Luso-IA</h3>", unsafe_allow_html=True)
    
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
             st.error("Demonstração terminada.")
             st.markdown(f"<a href='{LINK_TALLY}' target='_blank' style='display:block;text-align:center;background:#007AFF;color:white;padding:12px;border-radius:12px;text-decoration:none;font-weight:bold;'>Obter Acesso Ilimitado</a>", unsafe_allow_html=True)
        else:
            if st.button("Começar Demo"):
                st.session_state.user_type = "DEMO"
                st.rerun()
    return False

# --- APP ---
if check_login():
    col1, col2 = st.columns([1, 4])
    with col1:
        try: st.image("logo.png", width=80)
        except: st.write("🌍")
    with col2:
        st.markdown("<h2 style='margin:0; padding-top:10px; color: white !important;'>Luso-IA</h2>", unsafe_allow_html=True)
        if st.session_state.user_type != "PRO":
            usos_ip = usage_tracker.get(user_ip, 0)
            restantes = 3 - usos_ip
            if restantes <= 0:
                st.error("Limite atingido.")
                st.markdown(f"<a href='{LINK_TALLY}' target='_blank' style='display:block;text-align:center;background:#007AFF;color:white;padding:15px;border-radius:12px;text-decoration:none;'>Desbloquear App</a>", unsafe_allow_html=True)
                st.stop()

    try:
        if "GOOGLE_KEYS" not in st.secrets and "GOOGLE_API_KEY" not in st.secrets:
             st.error("Erro configuração.")
             st.stop()
    except: pass

    # --- SELETOR ESTILO iOS (CENTRADO) ---
    st.write("### Escolha a Plataforma")
    
    # Usei ícones quadrados com cantos redondos (estilo App Icon)
    rede_escolhida_idx = image_select(
        label="",
        images=[
            "https://cdn-icons-png.flaticon.com/512/3955/3955024.png", # Instagram (Square)
            "https://cdn-icons-png.flaticon.com/512/145/145807.png",   # LinkedIn (Square)
            "https://cdn-icons-png.flaticon.com/512/3670/3670151.png", # Twitter/X (Square)
            "https://cdn-icons-png.flaticon.com/512/3046/3046121.png", # TikTok (Square)
            "https://cdn-icons-png.flaticon.com/512/3670/3670147.png", # YouTube (Square)
            "https://cdn-icons-png.flaticon.com/512/3670/3670127.png", # Facebook (Square)
            "https://cdn-icons-png.flaticon.com/512/3670/3670051.png", # WhatsApp (Square)
            "https://cdn-icons-png.flaticon.com/512/10024/10024225.png" # Blog (Square)
        ],
        captions=["Instagram", "LinkedIn", "X", "TikTok", "YouTube", "Facebook", "WhatsApp", "Blog"],
        index=0,
        return_value="index",
        use_container_width=False # IMPORTANTE: False para permitir centralizar com CSS
    )

    redes_nomes = ["Instagram", "LinkedIn", "Twitter", "TikTok", "YouTube", "Facebook", "WhatsApp", "Blog"]
    rede_nome = redes_nomes[rede_escolhida_idx]

    with st.form("gerador"):
        st.write("### Detalhes")
        col_a, col_b = st.columns(2)
        with col_a: 
            pais = st.selectbox("País", ["🇵🇹 Portugal", "🇧🇷 Brasil", "🇦🇴 Angola", "🇲🇿 Moçambique", "🇨🇻 Cabo Verde", "🇬🇼 Guiné", "🇸🇹 São Tomé", "🇹🇱 Timor"])
        with col_b: 
            tom = st.selectbox("Tom", ["Profissional", "Divertido", "Vendas", "Storytelling", "Urgente"])
            
        negocio = st.text_input("Negócio:", placeholder="Ex: Café Central")
        tema = st.text_area("Tópico:", placeholder="Ex: Promoção de pequeno-almoço")
        btn = st.form_submit_button("Gerar Conteúdo")

    if btn and negocio:
        if st.session_state.user_type == "DEMO":
            current_usage = usage_tracker.get(user_ip, 0)
            if current_usage < 3:
                usage_tracker[user_ip] = current_usage + 1
                if usage_tracker[user_ip] >= 3: time.sleep(1)
            else: st.rerun()

        data_hoje = get_current_date()

        with st.spinner("A pensar..."):
            prompt = f"""
            Data Atual: {data_hoje}.
            Copywriter Expert. País: {pais}. Rede: {rede_nome}. Tom: {tom}. 
            Negócio: {negocio}. Tópico: {tema}. 
            Foco: Vendas e cultura local.
            """
            
            response, erro = gerar_conteudo_final(prompt)
            if response:
                st.markdown(response.text)
            else:
                st.error(f"Erro: {erro}")
                st.info("A tentar reconectar...")

        with st.spinner("A criar imagem..."):
            try:
                clean_keywords = f"{negocio} {tema}"
                try:
                    if response:
                        vis_resp, _ = gerar_conteudo_final(f"Identify 3 English keywords for a stock photo about: '{negocio} {tema}' in {pais}. Output ONLY words.")
                        if vis_resp: clean_keywords = vis_resp.text.strip()
                except: pass
                
                seed = random.randint(1, 999999)
                prompt_img = f"Professional product photography of {clean_keywords}, {pais} aesthetic, 4k, photorealistic, no text, object focused, no people"
                prompt_clean = urllib.parse.quote(prompt_img)
                url_img = f"https://image.pollinations.ai/prompt/{prompt_clean}?width=1024&height=1024&model=flux&seed={seed}&nologo=true"
                st.image(url_img, caption="Imagem IA")
                
                termo_safe = re.sub(r'[^\w\s]', '', clean_keywords).strip().replace(" ", "-")
                if not termo_safe: termo_safe = "business"
                st.markdown(f"<div style='text-align:center'><a href='https://unsplash.com/s/photos/{termo_safe}' target='_blank' style='color:#aaa; text-decoration:none; font-size:0.8em;'>🔍 Ver no Unsplash</a></div>", unsafe_allow_html=True)
            except: pass

    st.markdown("<br><br>", unsafe_allow_html=True)
