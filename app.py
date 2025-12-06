import streamlit as st
import google.generativeai as genai
import os

# CONFIGURAÇÃO VISUAL
st.set_page_config(page_title="Luso-IA Diagnóstico", page_icon="🛠️", layout="centered")

# --- SEGURANÇA (Senha: LUSOIA2025) ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    def password_entered():
        if st.session_state["password"] == "LUSOIA2025":
            st.session_state.password_correct = True
            del st.session_state["password"]
        else:
            st.session_state.password_correct = False
    if not st.session_state.password_correct:
        st.text_input("Senha de Acesso:", type="password", on_change=password_entered, key="password")
        return False
    else:
        return True

if check_password():
    col1, col2 = st.columns([1, 5])
    with col1:
        # Tenta carregar o logo, se não der, não faz mal
        try:
            st.image("logo.png", width=60)
        except:
            st.write("🚀")
    with col2:
        st.title("Luso-IA (Modo Estável)")

    # --- DIAGNÓSTICO DA CHAVE ---
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        # Esconde a chave, mostra só os ultimos 4 digitos para confirmar
        st.caption(f"Chave carregada: ...{api_key[-4:]}") 
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error(f"❌ Erro ao ler a API Key dos Secrets: {e}")
        st.stop()

    with st.form("gerador"):
        pais = st.selectbox("Mercado", ["Portugal (PT-PT)", "Brasil (PT-BR)", "Angola (PT-AO)"])
        negocio = st.text_input("Negócio:", placeholder="Ex: Café")
        tema = st.text_area("Tópico:", placeholder="Ex: Promoção")
        btn = st.form_submit_button("Testar Gerador")

    if btn and negocio:
        with st.spinner("A testar conexão à Google..."):
            try:
                # Vamos usar o modelo FLASH que é o mais rápido e gratuito
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                response = model.generate_content(f"Cria um post curto para {negocio} em {pais} sobre {tema}.")
                
                st.success("✅ SUCESSO! O sistema está a funcionar.")
                st.markdown(response.text)
                
            except Exception as e:
                # AQUI ESTÁ O QUE PRECISAMOS VER
                st.error("❌ Ocorreu um erro técnico:")
                st.code(e) # Isto vai mostrar o erro exato
                st.info("Copia a mensagem vermelha acima e envia para o suporte.")
