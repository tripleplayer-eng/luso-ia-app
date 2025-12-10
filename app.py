import streamlit as st
import google.generativeai as genai
import pandas as pd
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

# --- CSS PREMIUM (Design Apple Dark) ---
st.markdown("""
    <style>
        /* 1. INPUTS CLAROS (Para facilitar a escrita) */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
            background-color: #f8fafc !important; /* Cinza muito claro */
            color: #0f172a !important; /* Texto Escuro */
            border: 1px solid #cbd5e1 !important;
            border-radius: 10px !important;
        }
        /* Foco no input */
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 2px rgba(37,99,235,0.2) !important;
        }
        /* Labels (Títulos dos campos) em branco para contrastar com o fundo preto */
        .stTextInput label, .stTextArea label, .stSelectbox label {
            color: #e2e8f0 !important;
            font-weight: 600;
        }

        /* 2. ÍCONES FLUTUANTES (Estilo Cartão) */
        /* Remove as bolinhas dos radios */
        div[role="radiogroup"] > label > div:first-child {
            display: none;
        }
        div[role="radiogroup"] {
            gap: 12px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
        }
        div[role="radiogroup"] label {
            background-color: rgba(255, 255, 255, 0.05); /* Fundo vidro escuro */
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 15px 20px;
            border-radius: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: white !important;
            text-align: center;
            min-width: 100px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        /* Efeito Hover (Levitar) */
        div[role="radiogroup"] label:hover {
            background-color: rgba(255, 255, 255, 0.1);
            transform: translateY(-5px);
            border-color: #2563eb;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        }
        /* Item Selecionado */
        div[role="radiogroup"] label[data-checked="true"] {
            background: linear-gradient(135deg, #2563eb, #4f46e5);
            border-color: #4f46e5;
            box-shadow: 0 0 15px rgba(37, 99, 235, 0.5);
            font-weight: bold;
        }

        /* 3. LIMPEZA GERAL */
        header[data-testid="stHeader"] {visibility: hidden; height: 0px;}
        #MainMenu {visibility: hidden; display: none;}
        footer {visibility: hidden; display: none;}
        .block-container {padding-top: 2rem !important; padding-bottom: 5rem !important;}
        
        /* 4. BOTÃO DE AÇÃO */
        .stButton button { 
            width: 100%; border-radius: 12px; font-weight: 700; font-size: 1.1rem;
            background: linear-gradient(90deg, #2563eb, #4f46e5); color: white; border: none; padding: 0.8rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s;
        }
        .stButton button:hover { transform: scale(1.02); box-shadow: 0 6px 12px rgba(37, 99, 235, 0.4); }
    </style>
""", unsafe_allow_html=True)

# --- LINKS ---
LINK_DA_BASE_DE_DADOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_xyKHdsk9og2mRKE5uZBKcANNFtvx8wuUhR3a7gV-TFlZeSuU2wzJB_SjfkUKKIqVhh3LcaRr8Wn3/pub?gid=0&single=true&output=csv"
LINK_TALLY = "https://tally.so/r/81qLVx"

# --- MOTOR DE IA FIXO ---
MODELO_ESTAVEL = "gemini-1.5-flash"

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

# --- FUNÇÃO DE ROTAÇÃO DE CHAVES ---
def gerar_conteudo_seguro(prompt):
    keys = []
    if "GOOGLE_KEYS" in st.secrets: keys = st.secrets["GOOGLE_KEYS"]
    elif "GOOGLE_API_KEY" in st.secrets: keys = [st.secrets["GOOGLE_API_KEY"]]
    
    if not keys: return None
    random.shuffle(keys)
    
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(MODELO_ESTAVEL)
            response = model.generate_content(prompt)
            return response
        except exceptions.ResourceExhausted:
            continue
        except:
            continue
    return None

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
    
    tab1, tab2 = st.tabs(["🔑 Entrar (Pro)", "🎁 Testar (Grátis)"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email:")
            senha = st.text_input("Senha:", type="password")
            if st.form_submit_button("Entrar"):
                # --- LÓGICA DE ADMIN (AQUI ESTÁ O TRUQUE) ---
                if senha == "SOU-O-DONO":
                    st.session_state.user_type = "PRO"
                    st.session_state.user_email = "Admin"
                    st.success("⚡ Modo Administrador Ativado!")
                    time.sleep(0.5)
                    st.rerun()
                
                # Login Normal
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

# --- APP PRINCIPAL ---
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
        # Check rápido de chaves
        if "GOOGLE_KEYS" not in st.secrets and "GOOGLE_API_KEY" not in st.secrets:
             st.error("Erro: API Key em falta.")
             st.stop()
    except: pass

    # --- SELETOR DE REDES FLUTUANTES (NOVO DESIGN) ---
    st.write("### 📢 Publicar onde?")
    
    # Emojis funcionam melhor que imagens externas para carregar rápido e sem fundo branco
    rede_escolhida = st.radio(
        "Selecione:",
        ["📸 Instagram", "💼 LinkedIn", "🎵 TikTok", "📘 Facebook", "▶️ YouTube", "🐦 Twitter", "💬 WhatsApp", "📝 Blog"],
        horizontal=True,
        label_visibility="collapsed"
    )

    with st.form("gerador"):
        st.write("### ⚙️ Configuração")
        col_a, col_b = st.columns(2)
        with col_a: 
            pais = st.selectbox("País", ["🇵🇹 Portugal", "🇧🇷 Brasil", "🇦🇴 Angola", "🇲🇿 Moçambique", "🇨🇻 Cabo Verde", "🇬🇼 Guiné", "🇸🇹 São Tomé", "🇹🇱 Timor"])
        with col_b: 
            tom = st.selectbox("Tom", ["Profissional", "Divertido", "Vendas/Promoção", "Storytelling", "Urgente", "Inspirador", "Institucional"])
            
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

        # Limpeza do nome da rede (tirar emoji)
        rede_nome = rede_escolhida.split(" ")[1] 
        
        # Obter data atual
        meses = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}
        h = datetime.now()
        data_hoje = f"{h.day} de {meses[h.month]} de {h.year}"

        # 1. TEXTO
        with st.spinner("A escrever..."):
            prompt = f"""
            Data Atual: {data_hoje}.
            Atua como Copywriter Sénior da Luso-IA.
            País: {pais}. Rede: {rede_nome}. Tom: {tom}. 
            Negócio: {negocio}. Tópico: {tema}. 
            Objetivo: Criar conteúdo focado em vendas e cultura local.
            """
            response = gerar_conteudo_seguro(prompt)
            if response:
                st.markdown(response.text)
            else:
                st.error("⚠️ Erro de ligação. Tente novamente.")

        # 2. IMAGEM
        with st.spinner("A preparar imagens..."):
            try:
                # Prompt visual
                clean_keywords = f"{negocio} {tema}"
                try:
                    if response:
                        vis_resp = gerar_conteudo_seguro(f"Identify 3 English keywords for a stock photo about: '{negocio} {tema}' in {pais}. Output ONLY the 3 words.")
                        if vis_resp: clean_keywords = vis_resp.text.strip()
                except: pass
                
                # A. Imagem IA (Pollinations)
                seed = random.randint(1, 999999)
                prompt_img = f"Professional product photography of {clean_keywords}, {pais} aesthetic, cinematic lighting, 4k, photorealistic, no text, object focused, no people"
                prompt_clean = urllib.parse.quote(prompt_img)
                url_img = f"https://image.pollinations.ai/prompt/{prompt_clean}?width=1024&height=1024&model=flux&seed={seed}&nologo=true"
                
                st.image(url_img, caption="Imagem Gerada (IA)")
                
                # B. Link Unsplash
                termo_safe = re.sub(r'[^\w\s]', '', clean_keywords).strip().replace(" ", "-")
                if not termo_safe: termo_safe = "business"
                
                st.markdown(f"""
                    <a href="https://unsplash.com/s/photos/{termo_safe}" target="_blank" style="text-decoration:none;">
                        <button style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#1e293b;color:white;cursor:pointer;font-weight:bold;margin-top:10px;">
                            🔍 Ver fotos reais no Unsplash (Backup)
                        </button>
                    </a>
                """, unsafe_allow_html=True)
            except: pass

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; color: #64748b; font-size: 0.8rem;'>Luso-IA • {pais.split(' ')[1]}</div>", unsafe_allow_html=True)
