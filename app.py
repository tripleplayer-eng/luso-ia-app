import streamlit as st
import google.generativeai as genai
import os

# CONFIGURAÇÃO
st.set_page_config(page_title="Luso-IA System", page_icon="⚙️")

# --- SEGURANÇA ---
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
    st.title("Luso-IA: Painel de Controlo")

    # 1. AUTENTICAÇÃO
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        st.success("✅ Chave API conectada com sucesso.")
    except Exception as e:
        st.error(f"❌ Erro na Chave API: {e}")
        st.stop()

    # 2. LISTAR MODELOS DISPONÍVEIS (O "Caça-Modelos")
    st.info("🔄 A contactar a Google para ver modelos disponíveis...")
    
    try:
        lista_modelos = []
        for m in genai.list_models():
            # Filtra apenas os que geram texto
            if 'generateContent' in m.supported_generation_methods:
                # Limpa o nome (tira o 'models/')
                nome_limpo = m.name.replace('models/', '')
                lista_modelos.append(nome_limpo)
        
        if not lista_modelos:
            st.error("⚠️ A Google não devolveu nenhum modelo. A Chave API pode não ter permissões.")
            st.stop()
            
    except Exception as e:
        st.error(f"❌ Erro ao listar modelos: {e}")
        st.stop()

    # 3. INTERFACE DE GERAÇÃO
    with st.form("debug_form"):
        st.write("### Teste de Geração")
        
        # AQUI ESTÁ A SOLUÇÃO: Tu escolhes o modelo da lista real!
        modelo_escolhido = st.selectbox("Escolha o Modelo:", lista_modelos)
        
        tema = st.text_input("Tema para teste:", value="Diz Olá Mundo em Português")
        btn = st.form_submit_button("Testar Agora")

    if btn:
        with st.spinner(f"A testar com {modelo_escolhido}..."):
            try:
                model = genai.GenerativeModel(modelo_escolhido)
                response = model.generate_content(tema)
                
                st.success("🎉 FUNCIONOU!")
                st.markdown(f"**Resposta da IA:** {response.text}")
                
            except Exception as e:
                st.error("❌ Erro na geração:")
                st.code(e)

