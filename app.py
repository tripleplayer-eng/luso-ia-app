import streamlit as st
import google.generativeai as genai

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Luso-IA Global", page_icon="🌍")

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
        st.text_input("Senha:", type="password", on_change=password_entered, key="password")
        return False
    return True

# --- FUNÇÃO QUE ENCONTRA O MODELO QUE FUNCIONA ---
def get_working_model():
    """Testa qual o modelo disponível para esta conta/região."""
    try:
        # 1. Pede a lista à Google
        lista = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                name = m.name.replace('models/', '')
                lista.append(name)
        
        # 2. Tenta encontrar os melhores por ordem de preferência
        preferidos = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-pro"]
        
        for modelo in preferidos:
            if modelo in lista:
                return modelo
        
        # 3. Se nenhum preferido existir, devolve o primeiro da lista geral
        if lista:
            return lista[0]
            
        return "gemini-pro" # Fallback final
        
    except:
        return "gemini-pro"

# --- APP ---
if check_password():
    col1, col2 = st.columns([1,4])
    with col1:
        try: st.image("logo.png", use_container_width=True)
        except: st.write("🌍")
    with col2:
        st.title("Luso-IA Global")

    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # AQUI ESTÁ A SOLUÇÃO: Deteta o modelo automaticamente
        modelo_ativo = get_working_model()
        
    except:
        st.error("Erro na API Key.")
        st.stop()

    st.success(f"✅ Sistema conectado. Motor ativo: {modelo_ativo}")

    with st.form("gerador"):
        pais = st.selectbox("País", ["Portugal", "Brasil", "Angola", "Moçambique", "Cabo Verde"])
        tom = st.selectbox("Tom", ["Profissional", "Divertido", "Vendas"])
        negocio = st.text_input("Negócio:", placeholder="Ex: Clínica em Braga")
        tema = st.text_area("Tópico:", placeholder="Ex: Promoção")
        btn = st.form_submit_button("Gerar Conteúdo")

    if btn and negocio:
        with st.spinner("A gerar..."):
            prompt = f"Atua como copywriter para {pais}. Negócio: {negocio}. Tom: {tom}. Tópico: {tema}. Cria um post Instagram."
            try:
                model = genai.GenerativeModel(modelo_ativo)
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro: {e}")





