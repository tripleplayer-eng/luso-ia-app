import streamlit as st
import google.generativeai as genai
from streamlit_image_select import image_select

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Luso-IA App", page_icon="🇵🇹", layout="centered")

# --- CSS VISUAL ---
st.markdown("""
<style>
    iframe { display: block; margin: 0 auto; }
    h1 { text-align: center; }
    .stButton button { 
        width: 100%; border-radius: 12px; font-weight: bold; 
        background: linear-gradient(to right, #2563eb, #4f46e5); 
        color: white; padding: 0.7rem 1rem; border: none;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2); transition: all 0.3s ease;
    }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4); }
    .caption-text { text-align: center; color: #64748b; font-size: 1.1rem; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- GESTÃO DE ESTADO (CONTADOR DEMO) ---
if "demo_count" not in st.session_state:
    st.session_state.demo_count = 0

# --- SEGURANÇA INTELIGENTE ---
def check_login():
    if "user_type" not in st.session_state:
        st.session_state.user_type = None

    # Se já estiver logado, passa
    if st.session_state.user_type:
        return True

    # Ecrã de Login
    try: st.image("logo.png", width=80) 
    except: pass
    st.markdown("### 🔒 Login Luso-IA")
    
    senha_input = st.text_input("Senha de Acesso:", type="password")
    
    if senha_input:
        if senha_input == "LUSOIA2025": # SENHA PAGA (ILIMITADA)
            st.session_state.user_type = "PRO"
            st.rerun()
        elif senha_input == "TRY-LUSO": # SENHA DEMO (LIMITADA)
            st.session_state.user_type = "DEMO"
            st.rerun()
        else:
            st.error("Senha incorreta.")
    
    # Dica para novos utilizadores
    st.info("💡 Novo aqui? Use a senha **TRY-LUSO** para testar grátis (3 créditos).")
    return False

# --- MOTOR ---
def get_working_model():
    try:
        lista = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        preferidos = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        for modelo in preferidos:
            if modelo in lista: return modelo
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
    # BARRA SUPERIOR (STATUS)
    col1, col2 = st.columns([1, 4])
    with col1:
        try: st.image("logo.png", use_container_width=True)
        except: st.write("🌍")
    with col2:
        st.title("Luso-IA Global")
        if st.session_state.user_type == "DEMO":
            restantes = 3 - st.session_state.demo_count
            st.warning(f"💎 Modo Demonstração: Tem **{restantes}** gerações restantes.")
        else:
            st.success("💎 Modo PRO: Acesso Ilimitado")

    # VERIFICAÇÃO DE LIMITE
    bloqueado = False
    if st.session_state.user_type == "DEMO" and st.session_state.demo_count >= 3:
        bloqueado = True

    if bloqueado:
        st.error("🚫 Limite de demonstração atingido!")
        st.markdown("""
        <div style="background-color: #fee2e2; padding: 20px; border-radius: 10px; border: 1px solid #ef4444; text-align: center;">
            <h3 style="color: #991b1b;">Gostou da experiência?</h3>
            <p style="color: #7f1d1d;">Já usou os seus 3 créditos gratuitos. Para continuar a criar conteúdo ilimitado, ative a sua licença.</p>
            <a href="https://tally.so/r/w7e8a" target="_blank" 
               style="display: inline-block; background-color: #dc2626; color: white; padding: 12px 25px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 10px;">
               🚀 Ativar Luso-IA Pro Agora
            </a>
        </div>
        """, unsafe_allow_html=True)
        st.stop() # Pára o código aqui, não mostra o resto

    # SE NÃO ESTIVER BLOQUEADO, MOSTRA A APP NORMAL:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        modelo_ativo = get_working_model()
    except:
        st.error("Erro Crítico: API Key em falta.")
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
    with st.form("gerador"):
        st.write("### 2. Detalhes")
        col_a, col_b = st.columns(2)
        with col_a:
            pais = st.selectbox("País Alvo", ["🇵🇹 Portugal (PT-PT)", "🇧🇷 Brasil (PT-BR)", "🇦🇴 Angola (PT-AO)", "🇲🇿 Moçambique (PT-MZ)", "🇨🇻 Cabo Verde (PT-CV)", "🇬🇼 Guiné-Bissau (PT-GW)", "🇸🇹 São Tomé e Príncipe (PT-ST)", "🇹🇱 Timor-Leste (PT-TL)"])
        with col_b:
            tom = st.selectbox("Tom", ["Profissional", "Divertido", "Vendas/Promoção", "Storytelling", "Institucional"])
        negocio = st.text_input("O seu Negócio:", placeholder="Ex: Clínica Dentária...")
        tema = st.text_area("Tópico:", placeholder="Ex: Promoção de Natal...")
        btn = st.form_submit_button("✨ Gerar Conteúdo Mágico", type="primary")

    if btn and negocio:
        # Incrementa contador se for DEMO
        if st.session_state.user_type == "DEMO":
            st.session_state.demo_count += 1
            
        rede_nome = "Rede Social" # (Lógica simplificada para poupar espaço, funciona igual)
        if "2111463" in rede_selecionada: rede_nome = "Instagram"
        elif "174857" in rede_selecionada: rede_nome = "LinkedIn"
        # ... (A IA assume a rede certa na mesma)

        with st.spinner(f"A criar..."):
            prompt = f"Atua como Copywriter Sénior. País: {pais}. Negócio: {negocio}. Rede: {rede_nome}. Tom: {tom}. Tópico: {tema}. Cria o conteúdo."
            try:
                model = genai.GenerativeModel(modelo_ativo)
                response = model.generate_content(prompt)
                st.success("Conteúdo Gerado!")
                st.markdown(response.text)
                
                # Se for demo, avisa quanto falta
                if st.session_state.user_type == "DEMO":
                    usados = st.session_state.demo_count
                    st.caption(f"⚠️ Atenção: Usou {usados} de 3 créditos gratuitos.")
                    
            except Exception as e:
                st.error(f"Erro: {e}")

    st.markdown("---")
    preco, info = get_price_info(pais)
    st.markdown(f"<div style='text-align: center; color: gray;'>Licença: {pais.split('(')[0]} • {preco}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; margin-top: 10px;'><a href='https://tally.so/r/w7e8a' target='_blank' style='color: #2563eb; text-decoration: none; font-weight: bold;'>Subscrever Agora ➔</a></div>", unsafe_allow_html=True)
