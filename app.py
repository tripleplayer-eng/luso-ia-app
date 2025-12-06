import streamlit as st
import google.generativeai as genai

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Luso-IA Global", page_icon="🌍", layout="centered")

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
        # Tenta mostrar o logo
        try:
            st.image("logo.png", width=80)
        except:
            pass
        st.markdown("### 🔒 Acesso Restrito: Luso-IA")
        st.text_input("Senha de Acesso:", type="password", on_change=password_entered, key="password")
        return False
    else:
        return True

# --- MOTOR DE IA BLINDADO ---
# Mudámos para o FLASH. É o mais rápido e estável da Google atualmente.
MODELO_ESTAVEL = "gemini-1.5-flash"

# --- LÓGICA DE PREÇOS (PPP) ---
def get_price_info(pais_selecionado):
    if "Portugal" in pais_selecionado:
        return "29€", "Faturação Europeia"
    elif "Brasil" in pais_selecionado:
        return "R$ 97", "Preço especial Brasil"
    elif "Angola" in pais_selecionado:
        return "15.000 AOA", "Ajustado (Kwanza)"
    elif "Moçambique" in pais_selecionado:
        return "1.100 MZN", "Ajustado (Metical)"
    elif "Cabo Verde" in pais_selecionado:
        return "1.500 CVE", "Ajustado (Escudo)"
    elif "São Tomé" in pais_selecionado:
        return "350 STN", "Ajustado (Dobra)"
    else:
        return "~14€ (Equivalente)", "Preço Global South"

if check_password():
    # --- CABEÇALHO ---
    col_logo, col_text = st.columns([1, 4])
    with col_logo:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.write("🌍")
    with col_text:
        st.title("Luso-IA Global")
        st.caption("A Inteligência Artificial da Lusofonia")
    
    # Configuração API
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except:
        st.error("Erro Crítico: API Key não configurada.")
        st.stop()

    # Badge do Motor
    st.markdown(f"""
    <div style="background-color: #0f172a; color: #38bdf8; padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 20px; font-size: 0.8rem; border: 1px solid #1e293b;">
        ⚡ Motor Rápido Ativo: <code>{MODELO_ESTAVEL}</code>
    </div>
    """, unsafe_allow_html=True)

    # Formulário
    with st.form("gerador"):
        col1, col2 = st.columns(2)
        with col1:
            pais = st.selectbox(
                "Onde está o seu negócio?", 
                [
                    "Portugal (PT-PT)", 
                    "Brasil (PT-BR)", 
                    "Angola (PT-AO)", 
                    "Moçambique (PT-MZ)", 
                    "Cabo Verde (PT-CV)",
                    "Guiné-Bissau (PT-GW)",
                    "São Tomé e Príncipe (PT-ST)",
                    "Timor-Leste (PT-TL)"
                ]
            )
        with col2:
            tom = st.selectbox("Estilo", ["Inovador", "Profissional", "Viral", "Storytelling", "Institucional"])
            
        negocio = st.text_input("Negócio:", placeholder="Ex: Café Central em Luanda")
        tema = st.text_area("Tópico:", placeholder="Ex: Promoção de pequeno-almoço")
        
        btn = st.form_submit_button("🌍 Gerar Conteúdo Localizado")

    # Geração
    if btn and negocio and tema:
        with st.spinner(f"A criar conteúdo com sotaque de {pais}..."):
            
            prompt = f"""
            Atua como Copywriter Especialista na Lusofonia. 
            Estás a usar o modelo {MODELO_ESTAVEL}.
            
            DADOS:
            - Mercado: {pais}
            - Negócio: {negocio}
            - Tom: {tom}
            - Tópico: {tema}
            
            REGRAS DE OURO: 
            1. Usa a moeda correta do país selecionado se falares de preços.
            2. Usa a gramática correta (PT-BR para Brasil, PT-PT Base para o resto).
            3. Usa referências culturais locais se possível.
            
            SAÍDA: Post Instagram completo (Texto + Imagem + Hashtags).
            """
            
            try:
                model = genai.GenerativeModel(MODELO_ESTAVEL)
                response = model.generate_content(prompt)
                st.success("Gerado com sucesso!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro: {e}")

    # --- ÁREA DE VENDA ---
    st.markdown("---")
    
    preco_certo, info_extra = get_price_info(pais)
    
    st.markdown(f"""
    <div style="text-align: center; background-color: #f0f9ff; padding: 25px; border-radius: 12px; border: 1px solid #bae6fd;">
        <h3 style="color: #0c4a6e; margin:0; font-size: 1.2rem;">Gostou do resultado?</h3>
        <p style="color: #0369a1; font-size: 0.9rem; margin-bottom: 15px;">Esta é uma demonstração gratuita.</p>
        
        <div style="margin: 20px 0;">
            <p style="margin:0; font-size: 0.8rem; color: #64748b; text-transform: uppercase; font-weight:bold;">Preço para {pais.split('(')[0]}</p>
            <span style="font-size: 2rem; font-weight: 800; color: #0284c7;">{preco_certo}</span>
            <span style="font-size: 0.9rem; color: #64748b;">/mês</span>
            <p style="font-size: 0.8rem; color: #64748b;">({info_extra})</p>
        </div>
        
        <a href="https://www.luso-ia.com" target="_blank" 
           style="display: inline-block; background-color: #0284c7; color: white; padding: 14px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 10px; transition: 0.3s;">
           Garantir Oferta Local ➔
        </a>
    </div>
    """, unsafe_allow_html=True)




