import streamlit as st
import google.generativeai as genai
import pandas as pd
from streamlit_image_select import image_select
import time

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Luso-IA App", page_icon="🇵🇹", layout="centered")

# --- CSS ---
st.markdown("""
<style>
    .stButton button { width: 100%; border-radius: 12px; font-weight: bold; background: linear-gradient(to right, #2563eb, #4f46e5); color: white; padding: 0.7rem 1rem; border: none; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2); }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4); }
</style>
""", unsafe_allow_html=True)

# --- CONEXÃO À BASE DE DADOS (GOOGLE SHEETS) ---
# ⚠️ COLA AQUI O TEU LINK DO CSV ⚠️
LINK_DA_BASE_DE_DADOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_xyKHdsk9og2mRKE5uZBKcANNFtvx8wuUhR3a7gV-TFlZeSuU2wzJB_SjfkUKKIqVhh3LcaRr8Wn3/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def carregar_clientes():
    try:
        df = pd.read_csv(LINK_DA_BASE_DE_DADOS)
        df.columns = df.columns.str.strip()
        df['Email'] = df['Email'].astype(str).str.strip()
        df['Senha'] = df['Senha'].astype(str).str.strip()
        return dict(zip(df.Email, df.Senha))
    except:
        return {}

# --- SISTEMA DE LOGIN ---
def check_login():
    if "user_type" not in st.session_state:
        st.session_state.user_type = None

    if st.session_state.user_type:
        return True

    try: st.image("logo.png", width=80) 
    except: pass
    st.markdown("### 🔒 Login Luso-IA")
    
    # Apenas 2 Abas: Entrar ou Testar
    tab1, tab2 = st.tabs(["🔑 Entrar (Pro)", "🎁 Testar (Grátis)"])
    
    with tab1:
        with st.form("login_form_pro"):
            email_input = st.text_input("Email:").strip()
            senha_input = st.text_input("Senha:", type="password").strip()
            btn_pro = st.form_submit_button("Entrar")
            
            if btn_pro:
                clientes = carregar_clientes()
                if email_input in clientes and clientes[email_input] == senha_input:
                    st.session_state.user_type = "PRO"
                    st.session_state.user_email = email_input
                    st.success("Bem-vindo(a)!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Dados incorretos.")

    with tab2:
        st.info("Tem direito a 3 gerações gratuitas.")
        if st.button("Começar Demo"):
            st.session_state.user_type = "DEMO"
            st.rerun()

    return False

# --- MOTOR IA ---
def get_working_model():
    try:
        lista = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        preferidos = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        for m in preferidos:
            if m in lista: return m
        return lista[0] if lista else "gemini-pro"
    except: return "gemini-pro"

def get_price_info(pais):
    if "Portugal" in pais: return "19,90€", "Promoção Europa"
    if "Brasil" in pais: return "R$ 59,90", "Preço Brasil"
    if "Angola" in pais: return "12.000 Kz", "Preço Ajustado"
    if "Moçambique" in pais: return "590 MT", "Preço Ajustado"
    if "Cabo Verde" in pais: return "1.290$00", "Preço Ajustado"
    if "Guiné" in pais: return "6.500 XOF", "Preço Ajustado"
    if "São Tomé" in pais: return "350 STN", "Preço Ajustado"
    return "$12.00", "Internacional"

# --- APP ---
if check_login():
    col1, col2 = st.columns([1, 4])
    with col1:
        try: st.image("logo.png", use_container_width=True)
        except: st.write("🌍")
    with col2:
        st.title("Luso-IA Global")
        if st.session_state.user_type == "PRO":
            st.success(f"✅ Conta PRO: {st.session_state.user_email}")
        else:
            if "demo_count" not in st.session_state: st.session_state.demo_count = 0
            restantes = 3 - st.session_state.demo_count
            st.warning(f"⚠️ Demo: {restantes} créditos")

    if st.session_state.user_type == "DEMO" and st.session_state.demo_count >= 3:
        st.error("🚫 A sua demonstração terminou!")
        st.markdown("<a href='https://tally.so/r/81qLVx' target='_blank' style='background:#dc2626;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:bold;'>Subscrever Agora</a>", unsafe_allow_html=True)
        st.stop()

    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        modelo_ativo = get_working_model()
    except:
        st.error("Erro API Key.")
        st.stop()

    st.write("### 1. Onde vai publicar?")
    rede_selecionada = image_select(
        label="",
        images=[
            "https://cdn-icons-png.flaticon.com/512/2111/2111463.png", "https://cdn-icons-png.flaticon.com/512/733/733585.png",
            "https://cdn-icons-png.flaticon.com/512/174/174857.png", "https://cdn-icons-png.flaticon.com/512/1384/1384060.png",
            "https://cdn-icons-png.flaticon.com/512/3046/3046121.png", "https://cdn-icons-png.flaticon.com/512/5968/5968764.png",
            "https://cdn-icons-png.flaticon.com/512/5969/5969020.png", "https://cdn-icons-png.flaticon.com/512/4922/4922073.png",
        ],
        captions=["Instagram", "WhatsApp", "LinkedIn", "YouTube", "TikTok", "Facebook", "X / Twitter", "Blog"],
        index=0, use_container_width=False
    )

    st.markdown("---")
    with st.form("gerador_principal"): # Nome único para evitar erro de duplicado
        col_a, col_b = st.columns(2)
        with col_a:
            pais = st.selectbox("País Alvo", ["🇵🇹 Portugal (PT-PT)", "🇧🇷 Brasil (PT-BR)", "🇦🇴 Angola (PT-AO)", "🇲🇿 Moçambique (PT-MZ)", "🇨🇻 Cabo Verde (PT-CV)", "🇬🇼 Guiné-Bissau (PT-GW)", "🇸🇹 São Tomé e Príncipe (PT-ST)", "🇹🇱 Timor-Leste (PT-TL)"])
        with col_b:
            tom = st.selectbox("Tom", ["Profissional", "Divertido", "Vendas/Promoção", "Storytelling", "Institucional"])
        negocio = st.text_input("O seu Negócio:", placeholder="Ex: Clínica Dentária...")
        tema = st.text_area("Tópico:", placeholder="Ex: Promoção de Natal...")
        btn = st.form_submit_button("✨ Gerar Texto + Imagem IA")

    if btn and negocio:
        if st.session_state.user_type == "DEMO": st.session_state.demo_count += 1
        
        rede_nome = "Rede Social"
        if "2111463" in rede_selecionada: rede_nome = "Instagram"
        elif "733585" in rede_selecionada: rede_nome = "WhatsApp"
        elif "174857" in rede_selecionada: rede_nome = "LinkedIn"
        elif "1384060" in rede_selecionada: rede_nome = "YouTube"
        elif "3046121" in rede_selecionada: rede_nome = "TikTok"
        elif "5968764" in rede_selecionada: rede_nome = "Facebook"
        elif "5969020" in rede_selecionada: rede_nome = "Twitter"
        elif "4922073" in rede_selecionada: rede_nome = "Blog"

        # 1. TEXTO
        with st.spinner("✍️ A escrever..."):
            prompt = f"Atua como Copywriter. País: {pais}. Rede: {rede_nome}. Tom: {tom}. Negócio: {negocio}. Tópico: {tema}. Cria texto."
            try:
                model = genai.GenerativeModel(modelo_ativo)
                response = model.generate_content(prompt)
                st.success("Texto Gerado!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro Texto: {e}")

        # 2. IMAGEM IA
        with st.spinner("🎨 A criar imagem..."):
            try:
                # Prompt de imagem otimizado
                image_prompt = f"Professional photography of {tema} for {negocio}, {pais} context, high quality, {tom} style, 4k"
                image_prompt = image_prompt.replace(" ", "%20")
                image_url = f"https://image.pollinations.ai/prompt/{image_prompt}?width=800&height=800&nologo=true&seed={len(negocio)}"
                
                st.markdown("### 📸 Imagem Gerada pela Luso-IA")
                st.image(image_url)
                st.caption("Botão direito > Guardar imagem como...")
            except:
                st.warning("Não foi possível gerar a imagem.")

    st.markdown("---")
    p, i = get_price_info(pais)
    st.markdown(f"<div style='text-align: center; color: gray;'>Licença: {pais.split('(')[0]} • {p}</div>", unsafe_allow_html=True)
