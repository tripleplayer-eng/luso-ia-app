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

# --- MOTOR DE IA INTELIGENTE (AUTO-DESCOBERTA) ---
def get_best_model_name():
    """Pergunta à Google quais os modelos disponíveis e escolhe o melhor."""
    try:
        modelos_disponiveis = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                modelos_disponiveis.append(m.name.replace('models/', ''))
        
        # Lista de preferência (do melhor/mais barato para o mais antigo)
        preferencias = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-pro"]
        
        for p in preferencias:
            if p in modelos_disponiveis:
                return p
        
        # Se nenhum preferido existir, devolve o primeiro da lista
        return modelos_disponiveis[0] if modelos_disponiveis else "gemini-pro"
    except:
        return "gemini-pro" # Fallback de segurança máxima

# --- FUNÇÃO DE GERAÇÃO COM ROTAÇÃO DE CHAVES ---
def gerar_conteudo_seguro(prompt):
    try:
        keys = st.secrets["GOOGLE_KEYS"]
    except:
        # Se não houver lista, tenta chave única
        try: keys = [st.secrets["GOOGLE_API_KEY"]]
        except: return None

    random.shuffle(keys)
    nome_modelo = get_best_model_name() # Descobre o nome correto dinamicamente

    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(nome_modelo)
            response = model.generate_content(prompt)
            return response
        except exceptions.ResourceExhausted:
            continue # Tenta a próxima chave
        except Exception:
            continue
            
    return None

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

# --- DATA ---
def get_current_date():
    meses = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}
    hoje = datetime.now()
    return f"{hoje.day} de {meses[hoje.month]} de {hoje.year}"

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
                # Verifica admin local
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
             st.error("🚫 Já utilizou as suas 3 demonstrações gratuitas.")
             st.markdown(f"<a href='{LINK_TALLY}' target='_blank' style='display:block;text-align:center;background:#dc2626;color:white;padding:12px;border-radius:8px;text-decoration:none;font-weight:bold;'>Ativar Acesso Ilimitado</a>", unsafe_allow_html=True)
        else:
            restantes = 3 - usos_atuais
            st.info(f"Tem direito a {restantes} gerações neste dispositivo.")
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

    # Verifica se há chaves configuradas antes de começar
    try:
        if "GOOGLE_KEYS" not in st.secrets and "GOOGLE_API_KEY" not in st.secrets:
             st.error("Erro: Nenhuma API Key encontrada. Configure os Secrets.")
             st.stop()
    except: pass

    st.write("### Publicar onde?")
    rede_selecionada = image_select(
        label="",
        images=[
            "https://cdn-icons-png.flaticon.com/512/2111/2111463.png", 
            "https://cdn-icons-png.flaticon.com/512/174/174857.png", 
            "https://cdn-icons-png.flaticon.com/512/5968/5968764.png",
            "https://cdn-icons-png.flaticon.com/512/3046/3046121.png",
            "https://cdn-icons-png.flaticon.com/512/1384/1384060.png",
            "https://cdn-icons-png.flaticon.com/512/5969/5969020.png",
            "https://cdn-icons-png.flaticon.com/512/4922/4922073.png",
            "https://cdn-icons-png.flaticon.com/512/733/733585.png"
        ],
        captions=["Instagram", "LinkedIn", "Facebook", "TikTok", "YouTube", "X (Twitter)", "Blog", "WhatsApp"],
        index=0, use_container_width=False
    )

    with st.form("gerador"):
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

        rede_nome = "Rede Social"
        if "2111463" in rede_selecionada: rede_nome = "Instagram"
        elif "174857" in rede_selecionada: rede_nome = "LinkedIn"
        elif "5968764" in rede_selecionada: rede_nome = "Facebook"
        elif "3046121" in rede_selecionada: rede_nome = "TikTok"
        elif "1384060" in rede_selecionada: rede_nome = "YouTube"
        elif "5969020" in rede_selecionada: rede_nome = "Twitter"
        elif "4922073" in rede_selecionada: rede_nome = "Blog"
        elif "733585" in rede_selecionada: rede_nome = "WhatsApp"

        data_hoje = get_current_date()

        # 1. TEXTO
        with st.spinner("A escrever..."):
            prompt = f"""
            Data Atual: {data_hoje}.
            Atua como Copywriter Sénior da Luso-IA.
            País: {pais}. Rede: {rede_nome}. Tom: {tom}. 
            Negócio: {negocio}. Tópico: {tema}. 
            Objetivo: Criar conteúdo focado em vendas e cultura local.
            """
            
            # CHAMA A FUNÇÃO DE ROTAÇÃO INTELIGENTE
            response = gerar_conteudo_seguro(prompt)
            
            if response:
                st.markdown(response.text)
            else:
                st.error("⚠️ Erro de ligação à IA. Por favor, tente novamente em alguns segundos.")

        # 2. IMAGEM
        with st.spinner("A preparar imagens..."):
            try:
                # Usa a mesma função segura para as keywords
                prompt_visual = f"Identify 3 English keywords for a stock photo about: '{negocio} {tema}' in {pais}. Output ONLY the 3 words."
                visual_response = gerar_conteudo_seguro(prompt_visual)
                
                clean_keywords = ""
                if visual_response:
                    clean_keywords = visual_response.text.strip()
                else:
                    clean_keywords = f"{negocio} {tema}"
                
                # A. Imagem IA
                seed = random.randint(1, 999999)
                prompt_img = f"Professional product photography of {clean_keywords}, {pais} aesthetic, cinematic lighting, 4k, photorealistic, no text, object focused, no people"
                prompt_clean = urllib.parse.quote(prompt_img)
                url_img = f"https://image.pollinations.ai/prompt/{prompt_clean}?width=1024&height=1024&model=flux&seed={seed}&nologo=true"
                
                st.image(url_img, caption="Imagem Gerada (IA)")
                
                # B. Link Unsplash
                search_term = urllib.parse.quote(clean_keywords)
                st.markdown(f"""
                    <a href="https://unsplash.com/s/photos/{search_term}" target="_blank" style="text-decoration:none;">
                        <button style="width:100%;padding:10px;border-radius:8px;border:1px solid #ccc;background:white;color:#333;cursor:pointer;font-weight:bold;">
                            🔍 Ver fotos reais no Unsplash (Backup)
                        </button>
                    </a>
                """, unsafe_allow_html=True)
                
            except: 
                pass

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; color: #ccc; font-size: 0.8rem;'>Luso-IA • {pais.split(' ')[1]}</div>", unsafe_allow_html=True)
