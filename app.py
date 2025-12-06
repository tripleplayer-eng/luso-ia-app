import streamlit as st
import google.generativeai as genai

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Luso-IA Global", page_icon="🌍", layout="centered")

# --- SEGURANÇA ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    def password_entered():
        if st.session_state["password"] == "LUSOIA2025":
            st.session_state.password_correct = True
            del st.session_state["password"]
    if not st.session_state.password_correct:
        try: st.image("logo.png", width=80) 
        except: pass
        st.text_input("Senha de Acesso:", type="password", on_change=password_entered, key="password")
        return False
    return True

# --- MOTOR ---
def get_working_model():
    try:
        lista = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        preferidos = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        for modelo in preferidos:
            if modelo in lista: return modelo
        return lista[0] if lista else "gemini-pro"
    except: return "gemini-pro"

# --- APP ---
if check_password():
    col1, col2 = st.columns([1,4])
    with col1:
        try: st.image("logo.png", use_container_width=True)
        except: st.write("🌍")
    with col2:
        st.title("Luso-IA Global")
        st.caption("Geração de Conteúdo Multi-Plataforma")

    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        modelo_ativo = get_working_model()
    except:
        st.error("Erro na API Key.")
        st.stop()

    st.success(f"✅ Motor Ativo: {modelo_ativo}")

    with st.form("gerador"):
        col1, col2 = st.columns(2)
        with col1:
            pais = st.selectbox("País Alvo", ["Portugal", "Brasil", "Angola", "Moçambique", "Cabo Verde"])
            # NOVO: ESCOLHA DA REDE SOCIAL
            rede = st.selectbox("Rede Social", ["Instagram", "LinkedIn", "Facebook", "Blog Post", "TikTok (Guião)"])
        with col2:
            tom = st.selectbox("Tom de Voz", ["Profissional", "Divertido", "Vendas/Promoção", "Storytelling"])
            negocio = st.text_input("O seu Negócio:", placeholder="Ex: Advogado, Clínica, Loja...")
            
        tema = st.text_area("Sobre o que quer publicar?", placeholder="Ex: Dicas para poupar IRS ou Promoção de Verão")
        
        btn = st.form_submit_button("🚀 Gerar Conteúdo")

    if btn and negocio:
        with st.spinner(f"A criar post para {rede} em {pais}..."):
            # PROMPT MAIS AVANÇADO
            prompt = f"""
            Atua como Gestor de Redes Sociais Sénior.
            País: {pais}. Negócio: {negocio}. Tom: {tom}. Rede Social: {rede}.
            Tópico: {tema}.
            
            REGRAS ESPECÍFICAS PARA {rede}:
            - Se for LinkedIn: Sê profissional, usa parágrafos curtos, foco em autoridade.
            - Se for Instagram: Usa emojis, linguagem visual, hashtags no fim.
            - Se for TikTok: Cria um guião passo-a-passo para vídeo.
            
            Moeda/Cultura: Adapta ao país {pais}.
            """
            try:
                model = genai.GenerativeModel(modelo_ativo)
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.info("💡 Dica: Clique no ícone de copiar no canto superior direito do texto para colar na rede social.")
            except Exception as e:
                st.error(f"Erro: {e}")






