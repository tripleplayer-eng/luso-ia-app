import streamlit as st
import google.generativeai as genai
import pandas as pd
from streamlit_image_select import image_select
import time
import random
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Luso-IA App", 
    page_icon="🇵🇹", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS MÁGICO (REMOVE RODAPÉS E MELHORA UI) ---
st.markdown("""
    <style>
        /* Esconder Menu Hamburguer e Rodapé do Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Melhorar Botões */
        .stButton button { 
            width: 100%; 
            border-radius: 12px; 
            font-weight: 600; 
            background: linear-gradient(90deg, #2563eb, #4f46e5); 
            color: white; 
            border: none;
            padding: 0.8rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stButton button:hover { 
            transform: scale(1.02); 
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        
        /* Espaço extra no fundo para mobile */
        .block-container {
            padding-bottom: 5rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- LINKS ---
LINK_DA_BASE_DE_DADOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_xyKHdsk9og2mRKE5uZBKcANNFtvx8wuUhR3a7gV-TFlZeSuU2wzJB_SjfkUKKIqVhh3LcaRr8Wn3/pub?gid=0&single=true&output=csv"
LINK_TALLY = "https://tally.so/r/81qLVx"

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
    except:
        return {}

# --- LOGIN ---
def check_login():
    if "user_type" not in st.session_state:
        st.session_state.user_type = None

    if st.session_state.user_type:
        return True

    try: st.image("logo.png", width=80) 
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
                else:
                    st.error("Dados incorretos.")
    
    with tab2:
        st.info("3 Gerações Gratuitas")
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
        try: st.image("logo.png", use_container_width=True)
        except: st.write("🌍")
    with col2:
        st.title("Luso-IA")
        if st.session_state.user_type == "PRO":
            st.success("✅ Modo PRO Ativo")
        else:
            if "demo_count" not in st.session_state: st.session_state.demo_count = 0
            restantes = 3 - st.session_state.demo_count
            st.warning(f"⚠️ Demo: {restantes} restantes")

    if st.session_state.user_type == "DEMO" and st.session_state.demo_count >= 3:
        st.error("Demonstração terminada.")
        st.markdown(f"<a href='{LINK_TALLY}' target='_blank' style='display:block;text-align:center;background:#dc2626;color:white;padding:10px;border-radius:8px;text-decoration:none;'>Subscrever Agora</a>", unsafe_allow_html=True)
        st.stop()

    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        modelo_ativo = get_working_model()
    except:
        st.error("Erro API Key.")
        st.stop()

    st.write("### Publicar onde?")
    rede_selecionada = image_select(
        label="",
        images=[
            "https://cdn-icons-png.flaticon.com/512/2111/2111463.png", 
            "https://cdn-icons-png.flaticon.com/512/174/174857.png", 
            "https://cdn-icons-png.flaticon.com/512/1384/1384060.png",
            "https://cdn-icons-png.flaticon.com/512/5968/5968764.png", 
            "https://cdn-icons-png.flaticon.com/512/733/733585.png"
        ],
        captions=["Instagram", "LinkedIn", "YouTube", "Facebook", "WhatsApp"],
        index=0, use_container_width=False
    )

    with st.form("gerador"):
        col_a, col_b = st.columns(2)
        with col_a:
            pais = st.selectbox("País", ["🇵🇹 Portugal", "🇧🇷 Brasil", "🇦🇴 Angola", "🇲🇿 Moçambique", "🇨🇻 Cabo Verde", "🇬🇼 Guiné", "🇸🇹 São Tomé", "🇹🇱 Timor"])
        with col_b:
            tom = st.selectbox("Tom", ["Profissional", "Vendas", "Storytelling"])
        negocio = st.text_input("Negócio:", placeholder="Ex: Café Central")
        tema = st.text_area("Tópico:", placeholder="Ex: Promoção de pequeno-almoço")
        btn = st.form_submit_button("✨ Criar Conteúdo")

    if btn and negocio:
        if st.session_state.user_type == "DEMO": st.session_state.demo_count += 1
        
        rede_nome = "Rede Social"
        if "2111463" in rede_selecionada: rede_nome = "Instagram"
        elif "174857" in rede_selecionada: rede_nome = "LinkedIn"
        elif "1384060" in rede_selecionada: rede_nome = "YouTube"
        elif "5968764" in rede_selecionada: rede_nome = "Facebook"
        elif "733585" in rede_selecionada: rede_nome = "WhatsApp"

        with st.spinner("A escrever..."):
            prompt = f"Copywriter Expert. País: {pais}. Rede: {rede_nome}. Tom: {tom}. Negócio: {negocio}. Tópico: {tema}. Cria texto focado em vendas e cultura local."
            try:
                model = genai.GenerativeModel(modelo_ativo)
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro Texto: {e}")

        # --- GERAÇÃO DE IMAGEM MELHORADA (FLUX REALISM) ---
        with st.spinner("A gerar fotografia realista..."):
            try:
                seed = random.randint(1, 999999)
                # Prompt de Imagem Otimizado para evitar aberrações
                # Keywords: Photorealistic, 4k, no text, no blur, centered
                prompt_img = f"Photorealistic photo of {tema} inside a {negocio}, {pais} style context, natural lighting, high resolution, 4k, cinematic, highly detailed, no text, no watermark"
                prompt_clean = urllib.parse.quote(prompt_img)
                
                # URL Pollinations forçando modelo FLUX-REALISM
                url_img = f"https://image.pollinations.ai/prompt/{prompt_clean}?width=1024&height=1024&model=flux&seed={seed}&nologo=true"
                
                st.image(url_img, caption="Imagem Gerada (Flux AI)")
                st.caption("Dica: Botão direito para guardar.")
            except:
                st.warning("Imagem indisponível.")

    # --- ESPAÇO EXTRA NO FUNDO (PARA O TALLY NÃO TAPAR) ---
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; color: #ccc; font-size: 0.8rem;'>Luso-IA • {pais.split(' ')[1]}</div>", unsafe_allow_html=True)
