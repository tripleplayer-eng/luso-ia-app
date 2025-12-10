import streamlit as st
import google.generativeai as genai
import pandas as pd
import time
import random
from datetime import datetime
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx

# --- CONFIGURAÇÃO ---
st.set_page_config(
    page_title="Luso-IA", 
    page_icon="🇵🇹", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS CORREÇÃO VISUAL (BOTÕES QUADRADOS & RODAPÉ) ---
st.markdown("""
    <style>
        /* 1. FUNDO PRETO */
        .stApp { background-color: #000000; }
        h1, h2, h3, p, label, div, span { color: #e2e8f0 !important; }

        /* 2. REMOVER RODAPÉS (FORÇA BRUTA) */
        header {visibility: hidden; height: 0px;}
        footer {visibility: hidden; display: none !important;}
        #MainMenu {visibility: hidden; display: none;}
        .viewerBadge-container {display: none !important;} /* Remove "Built with Streamlit" */
        
        .block-container {
            padding-top: 1rem !important; 
            padding-bottom: 0rem !important;
        }

        /* 3. INPUTS */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #333 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        ul[data-testid="stSelectboxVirtualDropdown"] li {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* 4. GRELHA DE ÍCONES (FLEXBOX - NUNCA ESMAGA) */
        div[role="radiogroup"] {
            display: flex;
            flex-wrap: wrap; /* Permite cair para a linha de baixo */
            gap: 10px;
            justify-content: center;
        }
        
        div[role="radiogroup"] label > div:first-child { display: none; }

        /* ESTILO DO CARTÃO (FIXO) */
        div[role="radiogroup"] label {
            background-color: #111111 !important;
            border: 1px solid #333 !important;
            border-radius: 12px !important;
            width: 70px !important;       /* LARGURA FIXA */
            height: 70px !important;      /* ALTURA FIXA */
            min-width: 70px !important;   /* IMPEDE ESMAGAMENTO */
            display: flex !important;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            margin: 0 !important;
            /* Ícone */
            background-repeat: no-repeat;
            background-position: center;
            background-size: 35px; 
            opacity: 0.6;
            transition: all 0.2s;
        }

        div[role="radiogroup"] label p { display: none !important; }

        /* ÍCONES */
        div[role="radiogroup"] label:nth-child(1) { background-image: url('https://cdn-icons-png.flaticon.com/128/3955/3955024.png'); }
        div[role="radiogroup"] label:nth-child(2) { background-image: url('https://cdn-icons-png.flaticon.com/128/145/145807.png'); }
        div[role="radiogroup"] label:nth-child(3) { background-image: url('https://cdn-icons-png.flaticon.com/128/3670/3670151.png'); }
        div[role="radiogroup"] label:nth-child(4) { background-image: url('https://cdn-icons-png.flaticon.com/128/3046/3046121.png'); }
        div[role="radiogroup"] label:nth-child(5) { background-image: url('https://cdn-icons-png.flaticon.com/128/3670/3670147.png'); }
        div[role="radiogroup"] label:nth-child(6) { background-image: url('https://cdn-icons-png.flaticon.com/128/3670/3670127.png'); }
        div[role="radiogroup"] label:nth-child(7) { background-image: url('https://cdn-icons-png.flaticon.com/128/3670/3670051.png'); }
        div[role="radiogroup"] label:nth-child(8) { background-image: url('https://cdn-icons-png.flaticon.com/128/10024/10024225.png'); }

        /* SELECIONADO */
        div[role="radiogroup"] label[data-checked="true"] {
            background-color: rgba(37, 99, 235, 0.3) !important;
            border: 2px solid #2563eb !important;
            opacity: 1 !important;
            box-shadow: 0 0 10px rgba(37, 99, 235, 0.6);
            transform: scale(1.1);
        }
        
        div[role="radiogroup"] label:hover { opacity: 1; border-color: #555 !important; }

        /* 5. BOTÃO GERAR */
        .stButton button { 
            width: 100%; border-radius: 12px; font-weight: 800; font-size: 1.1rem;
            background: linear-gradient(90deg, #f59e0b, #d97706); 
            color: black !important; border: none; padding: 1rem;
            text-transform: uppercase; letter-spacing: 1px;
            margin-top: 15px;
        }
        .stButton button:hover { transform: scale(1.02); filter: brightness(1.1); }
    </style>
""", unsafe_allow_html=True)

# --- LINKS ---
LINK_DA_BASE_DE_DADOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_xyKHdsk9og2mRKE5uZBKcANNFtvx8wuUhR3a7gV-TFlZeSuU2wzJB_SjfkUKKIqVhh3LcaRr8Wn3/pub?gid=0&single=true&output=csv"
LINK_TALLY = "https://tally.so/r/81qLVx"

# --- MOTOR DE IA COM DIAGNÓSTICO ---
def gerar_conteudo_final(prompt):
    keys = []
    # Tenta ler chaves de todas as formas possíveis
    if "GOOGLE_KEYS" in st.secrets: keys = st.secrets["GOOGLE_KEYS"]
    elif "GOOGLE_API_KEY" in st.secrets: keys = [st.secrets["GOOGLE_API_KEY"]]
    
    if not keys: return None, "ERRO CRÍTICO: Não encontrei chaves API nos Secrets."
    
    random.shuffle(keys)
    modelos = ["gemini-1.5-flash", "gemini-pro"]
    
    erros_detalhados = []

    for modelo in modelos:
        for i, key in enumerate(keys):
            try:
                genai.configure(api_key=key)
                model_ai = genai.GenerativeModel(modelo)
                response = model_ai.generate_content(prompt)
                return response, None
            except Exception as e:
                erros_detalhados.append(f"Chave {i+1} ({modelo}): {str(e)}")
                continue

    # Se chegou aqui, falhou tudo. Retorna o erro técnico para leres.
    return None, str(erros_detalhados[0]) if erros_detalhados else "Erro desconhecido."

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
                        st.success("Admin")
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

    # --- SELETOR DE REDES (FLEXBOX) ---
    st.write("### 📢 Escolha a Plataforma")
    
    rede_escolhida = st.radio(
        "Selecione:",
        ["Instagram", "LinkedIn", "X (Twitter)", "TikTok", "YouTube", "Facebook", "WhatsApp", "Blog"],
        horizontal=True,
        label_visibility="collapsed"
    )

    with st.form("gerador"):
        st.write("### ⚙️ Detalhes")
        col_a, col_b = st.columns(2)
        with col_a: 
            pais = st.selectbox("País", ["🇵🇹 Portugal", "🇧🇷 Brasil", "🇦🇴 Angola", "🇲🇿 Moçambique", "🇨🇻 Cabo Verde", "🇬🇼 Guiné", "🇸🇹 São Tomé", "🇹🇱 Timor"])
        with col_b: 
            tom = st.selectbox("Tom", ["Profissional", "Divertido", "Vendas/Promoção", "Storytelling", "Urgente", "Inspirador", "Institucional"])
            
        negocio = st.text_input("Negócio:", placeholder="Ex: Café Central")
        tema = st.text_area("Tópico:", placeholder="Ex: Promoção de pequeno-almoço")
        btn = st.form_submit_button("✨ CRIAR CONTEÚDO")

    if btn and negocio:
        if st.session_state.user_type == "DEMO":
            current_usage = usage_tracker.get(user_ip, 0)
            if current_usage < 3:
                usage_tracker[user_ip] = current_usage + 1
                if usage_tracker[user_ip] >= 3: time.sleep(1)
            else: st.rerun()

        data_hoje = get_current_date()

        with st.spinner("A escrever..."):
            prompt = f"""
            Data Atual: {data_hoje}.
            Atua como Copywriter Sénior da Luso-IA.
            País: {pais}. Rede: {rede_escolhida}. Tom: {tom}. 
            Negócio: {negocio}. Tópico: {tema}. 
            Objetivo: Criar conteúdo focado em vendas e cultura local.
            """
            
            response, erro = gerar_conteudo_final(prompt)
            if response:
                st.markdown(response.text)
            else:
                # MOSTRA O ERRO REAL NO ECRÃ
                st.error(f"❌ Erro Técnico Google: {erro}")
                st.info("Copie este erro e envie ao suporte se persistir.")

        with st.spinner("A preparar imagens..."):
            try:
                clean_keywords = f"{negocio} {tema}"
                try:
                    if response:
                        vis_resp, _ = gerar_conteudo_final(f"Identify 3 English keywords for a stock photo about: '{negocio} {tema}' in {pais}. Output ONLY words.")
                        if vis_resp: clean_keywords = vis_resp.text.strip()
                except: pass
                
                # Pollinations
                seed = random.randint(1, 999999)
                prompt_img = f"Professional product photography of {clean_keywords}, {pais} aesthetic, cinematic lighting, 4k, photorealistic, no text, object focused, no people"
                prompt_clean = urllib.parse.quote(prompt_img)
                url_img = f"https://image.pollinations.ai/prompt/{prompt_clean}?width=1024&height=1024&model=flux&seed={seed}&nologo=true"
                st.image(url_img, caption="Imagem IA")
                
                # Unsplash Link Seguro
                # Remove emojis e caracteres especiais para não quebrar o link
                termo_safe = re.sub(r'[^\w\s]', '', clean_keywords).strip().replace(" ", "-")
                if not termo_safe: termo_safe = "business"
                
                st.markdown(f"<a href='https://unsplash.com/s/photos/{termo_safe}' target='_blank'><button style='width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#1e293b;color:white;cursor:pointer;font-weight:bold;margin-top:10px;'>🔍 Ver fotos reais no Unsplash (Backup)</button></a>", unsafe_allow_html=True)
            except: pass

    st.markdown("<br><br>", unsafe_allow_html=True)
