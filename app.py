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

# --- CSS PREMIUM (LOGÓTIPOS REAIS + DARK MODE) ---
st.markdown("""
    <style>
        /* 1. FUNDO GERAL */
        [data-testid="stAppViewContainer"] {
            background-color: #020617; /* Slate 950 */
        }
        
        /* 2. TEXTOS E TÍTULOS */
        h1, h2, h3, p, label, .stMarkdown, div { color: #e2e8f0 !important; }

        /* 3. INPUTS (CLAROS) */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
            background-color: #f8fafc !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 10px !important;
        }
        
        /* 4. SELETOR DE REDES (CARTÕES COM LOGÓTIPOS REAIS) */
        div[role="radiogroup"] > label > div:first-child { display: none; } /* Esconde bolinha */
        div[role="radiogroup"] {
            display: grid;
            grid-template-columns: repeat(4, 1fr); /* 4 colunas em PC */
            gap: 12px;
        }
        @media (max-width: 600px) {
            div[role="radiogroup"] { grid-template-columns: repeat(2, 1fr); } /* 2 colunas em mobile */
        }

        div[role="radiogroup"] label {
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            height: 110px; /* Altura fixa para caber o logo */
            display: flex;
            align-items: flex-end; /* Texto no fundo */
            justify-content: center;
            padding-bottom: 10px;
            background-repeat: no-repeat;
            background-position: center 20px; /* Logo no topo */
            background-size: 40px; /* Tamanho do logo */
            color: #94a3b8 !important;
            font-size: 0.8rem;
            font-weight: bold;
        }

        /* --- INJEÇÃO DOS LOGÓTIPOS (ORDEM DO MENU) --- */
        /* 1. Instagram */
        div[role="radiogroup"] label:nth-of-type(1) { background-image: url('https://cdn-icons-png.flaticon.com/128/174/174855.png'); }
        /* 2. LinkedIn */
        div[role="radiogroup"] label:nth-of-type(2) { background-image: url('https://cdn-icons-png.flaticon.com/128/3536/3536505.png'); }
        /* 3. TikTok */
        div[role="radiogroup"] label:nth-of-type(3) { background-image: url('https://cdn-icons-png.flaticon.com/128/3046/3046121.png'); background-size: 35px; }
        /* 4. Facebook */
        div[role="radiogroup"] label:nth-of-type(4) { background-image: url('https://cdn-icons-png.flaticon.com/128/5968/5968764.png'); }
        /* 5. YouTube */
        div[role="radiogroup"] label:nth-of-type(5) { background-image: url('https://cdn-icons-png.flaticon.com/128/1384/1384060.png'); }
        /* 6. Twitter/X */
        div[role="radiogroup"] label:nth-of-type(6) { background-image: url('https://cdn-icons-png.flaticon.com/128/5969/5969020.png'); background-size: 30px; }
        /* 7. WhatsApp */
        div[role="radiogroup"] label:nth-of-type(7) { background-image: url('https://cdn-icons-png.flaticon.com/128/733/733585.png'); }
        /* 8. Blog */
        div[role="radiogroup"] label:nth-of-type(8) { background-image: url('https://cdn-icons-png.flaticon.com/128/4922/4922073.png'); }

        /* HOVER (LEVITAR) */
        div[role="radiogroup"] label:hover {
            transform: translateY(-5px);
            background-color: rgba(255, 255, 255, 0.08);
            border-color: #3b82f6;
        }

        /* SELECIONADO (BRILHO AZUL) */
        div[role="radiogroup"] label[data-checked="true"] {
            background-color: rgba(37, 99, 235, 0.2);
            border-color: #3b82f6;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
            color: white !important;
        }

        /* LIMPEZA DE LAYOUT */
        header[data-testid="stHeader"] {visibility: hidden; height: 0px;}
        #MainMenu {display: none;}
        footer {display: none;}
        .block-container {padding-top: 1rem !important; padding-bottom: 5rem !important;}
        
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

# --- MOTOR DE IA "CAMALEÃO" (RESOLVE O 404) ---
def get_best_model():
    """Percorre a lista de modelos disponíveis na conta Google e escolhe o que funciona"""
    try:
        # Pede a lista real à Google
        available_models = [m.name.replace('models/', '') for m in genai.list_models()]
        
        # Ordem de preferência
        preference = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-pro"]
        
        for p in preference:
            if p in available_models: return p
            
        return "gemini-pro" # O mais antigo, funciona sempre
    except:
        return "gemini-pro"

# --- GERAÇÃO SEGURA ---
def gerar_conteudo_seguro(prompt):
    keys = []
    if "GOOGLE_KEYS" in st.secrets: keys = st.secrets["GOOGLE_KEYS"]
    elif "GOOGLE_API_KEY" in st.secrets: keys = [st.secrets["GOOGLE_API_KEY"]]
    
    if not keys: return None, "Sem chaves API"
    random.shuffle(keys)
    
    # Define o modelo uma vez
    model_name = get_best_model()
    
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response, None
        except Exception as e:
            continue # Tenta a próxima chave
            
    return None, f"Erro de conexão (Modelo: {model_name})"

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

    try: st.image("logo.png", width=200) 
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

    # --- SELETOR DE REDES (CSS STYLE) ---
    st.write("### 📢 Publicar onde?")
    
    # Nota: A ordem aqui tem de bater certo com a ordem do CSS lá em cima
    rede_escolhida = st.radio(
        "Selecione:",
        ["Instagram", "LinkedIn", "TikTok", "Facebook", "YouTube", "Twitter", "WhatsApp", "Blog"],
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

        data_hoje = get_current_date()

        # 1. TEXTO
        with st.spinner("A escrever..."):
            prompt = f"""
            Data Atual: {data_hoje}.
            Atua como Copywriter Sénior. País: {pais}. Rede: {rede_escolhida}. Tom: {tom}. 
            Negócio: {negocio}. Tópico: {tema}. 
            """
            
            response, erro = gerar_conteudo_seguro(prompt)
            if response:
                st.markdown(response.text)
            else:
                st.error(f"⚠️ Erro IA: {erro}")
                # Fallback de diagnóstico
                st.info(f"O modelo tentado foi: {get_best_model()}. Verifique se a API Key suporta este modelo.")

        # 2. IMAGEM
        with st.spinner("A preparar imagens..."):
            try:
                # Palavras-chave limpas
                clean_keywords = f"{negocio} {tema}"
                if response:
                    try:
                        vis_resp, _ = gerar_conteudo_seguro(f"Identify 3 English keywords for stock photo: '{negocio} {tema}'. Output ONLY words.")
                        if vis_resp: clean_keywords = vis_resp.text.strip()
                    except: pass
                
                # A. Imagem IA
                seed = random.randint(1, 999999)
                prompt_img = f"Professional product photography of {clean_keywords}, {pais} aesthetic, cinematic lighting, 4k, photorealistic, no text, object focused, no people"
                prompt_clean = urllib.parse.quote(prompt_img)
                url_img = f"https://image.pollinations.ai/prompt/{prompt_clean}?width=1024&height=1024&model=flux&seed={seed}&nologo=true"
                st.image(url_img, caption="Imagem Gerada (IA)")
                
                # B. Link Unsplash
                termo_safe = re.sub(r'[^\w\s]', '', clean_keywords).strip().replace(" ", "-")
                if not termo_safe: termo_safe = "business"
                st.markdown(f"<a href='https://unsplash.com/s/photos/{termo_safe}' target='_blank'><button style='width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#1e293b;color:white;cursor:pointer;font-weight:bold;margin-top:10px;'>🔍 Ver fotos reais no Unsplash</button></a>", unsafe_allow_html=True)
            except: pass

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; color: #64748b; font-size: 0.8rem;'>Luso-IA • {pais.split(' ')[1]}</div>", unsafe_allow_html=True)
