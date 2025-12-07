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
# ⚠️ COLA AQUI O TEU LINK DO CSV (Publicado na Web) ⚠️
LINK_DA_BASE_DE_DADOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_xyKHdsk9og2mRKE5uZBKcANNFtvx8wuUhR3a7gV-TFlZeSuU2wzJB_SjfkUKKIqVhh3LcaRr8Wn3/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=10) # Limpa a cache a cada 10 segundos para testares rápido
def carregar_clientes():
    try:
        # Lê o CSV
        df = pd.read_csv(LINK_DA_BASE_DE_DADOS)
        
        # LIMPEZA DE DADOS (CRÍTICO PARA FUNCIONAR)
        # Remove espaços em branco antes e depois dos textos
        df.columns = df.columns.str.strip() # Limpa cabeçalhos
        df['Email'] = df['Email'].astype(str).str.strip()
        df['Senha'] = df['Senha'].astype(str).str.strip()
        
        # Cria um dicionário {email: senha}
        return dict(zip(df.Email, df.Senha))
    except Exception as e:
        return {"erro": str(e)}

# --- SISTEMA DE LOGIN ---
def check_login():
    if "user_type" not in st.session_state:
        st.session_state.user_type = None

    if st.session_state.user_type:
        return True

    try: st.image("logo.png", width=80) 
    except: pass
    st.markdown("### 🔒 Login Luso-IA")
    
    tab1, tab2, tab3 = st.tabs(["🔑 Entrar (Pro)", "🎁 Testar (Grátis)", "🛠️ Admin"])
    
    # LOGIN PRO (COM DIAGNÓSTICO)
    with tab1:
        with st.form("login_pro"):
            email_input = st.text_input("O seu Email:").strip() # Remove espaços logo na entrada
            senha_input = st.text_input("A sua Senha:", type="password").strip()
            btn_pro = st.form_submit_button("Entrar")
            
            if btn_pro:
                clientes = carregar_clientes()
                
                # Verifica erro na leitura do Excel
                if "erro" in clientes:
                    st.error("Erro a ler base de dados. Verifique o link CSV no código.")
                
                # Validação
                elif email_input in clientes and clientes[email_input] == senha_input:
                    st.session_state.user_type = "PRO"
                    st.session_state.user_email = email_input
                    st.success("Login com sucesso!")
                    st.rerun()
                else:
                    st.error("Dados incorretos. Verifique o email e a senha.")
                    st.caption("Dica: A senha deve ser igual à que recebeu no email (Ex: LUSO-1234)")

    # DEMO
    with tab2:
        st.info("Tem direito a 3 gerações gratuitas.")
        if st.button("Começar Demo"):
            st.session_state.user_type = "DEMO"
            st.rerun()

    # ABA DE DIAGNÓSTICO (SÓ PARA TI - ELIMINAR DEPOIS SE QUISERES)
    with tab3:
        st.caption("Área secreta para verificar se o Excel está a funcionar.")
        if st.button("Ver Base de Dados (Debug)"):
            dados = carregar_clientes()
            st.write(dados)
            st.caption("Se vires os emails aqui, a conexão está a funcionar.")

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

    # SELETOR DE REDE
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
    with st.form("gerador"):
        col_a, col_b = st.columns(2)
        with col_a:
            pais = st.selectbox("País Alvo", ["🇵🇹 Portugal", "🇧🇷 Brasil", "🇦🇴 Angola", "🇲🇿 Moçambique", "🇨🇻 Cabo Verde", "🇬🇼 Guiné-Bissau", "🇸🇹 São Tomé", "🇹🇱 Timor-Leste"])
        with col_b:
            tom = st.selectbox("Tom", ["Profissional", "Divertido", "Vendas", "Storytelling"])
        negocio = st.text_input("O seu Negócio:")
        tema = st.text_area("Tópico:")
        btn = st.form_submit_button("✨ Gerar Texto + Imagem IA")

    if btn and negocio:
        if st.session_state.user_type == "DEMO": st.session_state.demo_count += 1
        
        rede_nome = "Instagram"
        if "174857" in rede_selecionada: rede_nome = "LinkedIn"
        elif "733585" in rede_selecionada: rede_nome = "WhatsApp"

        # 1. GERAÇÃO DE TEXTO
        with st.spinner("✍️ A escrever o copy..."):
            prompt = f"Atua como Copywriter. País: {pais}. Rede: {rede_nome}. Tom: {tom}. Negócio: {negocio}. Tópico: {tema}. Cria texto estruturado."
            try:
                model = genai.GenerativeModel(modelo_ativo)
                response = model.generate_content(prompt)
                st.success("Texto Gerado!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro Texto: {e}")

        # 2. GERAÇÃO DE IMAGEM (POLLINATIONS AI)
        with st.spinner("🎨 A pintar a imagem com IA..."):
            try:
                # Criamos um prompt de imagem simples em inglês para funcionar melhor
                image_prompt = f"Professional photography of {tema} for {negocio}, high quality, {tom} style, 4k"
                image_prompt = image_prompt.replace(" ", "%20") # Formata para URL
                
                # URL Mágico da Pollinations
                image_url = f"https://image.pollinations.ai/prompt/{image_prompt}?width=800&height=800&nologo=true"
                
                st.markdown("### 📸 Imagem Sugerida (IA)")
                st.image(image_url, caption="Imagem gerada por IA única para si.")
                st.info("Pode guardar esta imagem (Botão direito > Guardar como).")
                
            except Exception as e:
                st.warning("Não foi possível gerar a imagem neste momento.")


