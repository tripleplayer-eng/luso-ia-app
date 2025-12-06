import streamlit as st
import google.generativeai as genai
from streamlit_image_select import image_select # Nova ferramenta visual

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Luso-IA App", page_icon="🇵🇹", layout="centered")

# --- CSS PARA AJUSTES VISUAIS ---
st.markdown("""
<style>
    /* Ajuste para centrar o seletor de imagens */
    iframe { display: block; margin: 0 auto; }
    h1 { text-align: center; }
    .stButton button { width: 100%; border-radius: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

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
        st.markdown("### 🔒 Login Luso-IA")
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
if check_password():
    col1, col2 = st.columns([1, 4])
    with col1:
        try: st.image("logo.png", use_container_width=True)
        except: st.write("🌍")
    with col2:
        st.title("Luso-IA Global")
        st.caption("Selecione a rede clicando no ícone.")

    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        modelo_ativo = get_working_model()
    except:
        st.error("Erro Crítico: API Key em falta.")
        st.stop()

    # --- 1. SELETOR DE REDE COM ÍCONES REAIS ---
    st.write("### 1. Onde vai publicar?")
    
    # Lista de Ícones (Links diretos para Logótipos Oficiais)
    rede_selecionada = image_select(
        label="",
        images=[
            "https://upload.wikimedia.org/wikipedia/commons/e/e7/Instagram_logo_2016.svg",
            "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png",
            "https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg",
            "https://upload.wikimedia.org/wikipedia/commons/3/34/Icon_huset_whatsapp.svg",
            "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg",
            "https://upload.wikimedia.org/wikipedia/commons/c/ce/X_logo_2023.svg",
            "https://upload.wikimedia.org/wikipedia/commons/3/33/Figma-logo.svg", # Representando Blog/Design
        ],
        captions=["Instagram", "LinkedIn", "Facebook", "WhatsApp", "YouTube", "Twitter/X", "Blog/Outros"],
        index=0,
        use_container_width=False
    )

    # --- 2. FORMULÁRIO ---
    st.markdown("---")
    with st.form("gerador"):
        st.write("### 2. Detalhes")
        col_a, col_b = st.columns(2)
        with col_a:
            pais = st.selectbox("País Alvo", 
                ["Portugal (PT-PT)", "Brasil (PT-BR)", "Angola (PT-AO)", "Moçambique (PT-MZ)", 
                 "Cabo Verde (PT-CV)", "Guiné-Bissau (PT-GW)", "São Tomé e Príncipe (PT-ST)", "Timor-Leste (PT-TL)"])
        with col_b:
            tom = st.selectbox("Tom", ["Profissional", "Divertido", "Vendas/Promoção", "Storytelling", "Institucional"])
            
        negocio = st.text_input("O seu Negócio:", placeholder="Ex: Clínica Dentária, Loja de Roupa...")
        tema = st.text_area("Tópico do Conteúdo:", placeholder="Ex: Promoção de Natal ou Dicas de Prevenção")
        
        btn = st.form_submit_button("✨ Gerar Conteúdo Mágico", type="primary")

    # --- 3. RESULTADO ---
    if btn and negocio:
        # Traduzir o URL da imagem para o nome da rede (para o prompt)
        rede_nome = "Instagram" # Default
        if "Instagram" in rede_selecionada: rede_nome = "Instagram"
        elif "LinkedIn" in rede_selecionada: rede_nome = "LinkedIn"
        elif "Facebook" in rede_selecionada: rede_nome = "Facebook"
        elif "WhatsApp" in rede_selecionada: rede_nome = "WhatsApp"
        elif "YouTube" in rede_selecionada: rede_nome = "YouTube/TikTok"
        elif "X" in rede_selecionada: rede_nome = "Twitter/X"
        else: rede_nome = "Blog"

        with st.spinner(f"A criar para {rede_nome} em {pais}..."):
            
            prompt = f"""
            Atua como Copywriter Sénior. Modelo: {modelo_ativo}.
            
            CONTEXTO:
            - País: {pais}
            - Negócio: {negocio}
            - Rede: {rede_nome} (Baseado no ícone selecionado)
            - Tom: {tom}
            - Tópico: {tema}
            
            REGRAS ESPECÍFICAS ({rede_nome}):
            - Instagram: Visual, emojis, quebras de linha, hashtags no fim.
            - LinkedIn: Profissional, parágrafos curtos, sem hashtags excessivas.
            - Facebook: Comunitário, perguntas para engajamento.
            - YouTube/TikTok: GERA UM GUIÃO DE VÍDEO (Cena 1, Cena 2, Fala).
            - WhatsApp: Curto, direto, "Olá [Nome]", chamada para ação.
            - Blog: Título H1, introdução, pontos chave, conclusão SEO.
            
            CULTURA: Usa a moeda e gírias de {pais}.
            """
            
            try:
                model = genai.GenerativeModel(modelo_ativo)
                response = model.generate_content(prompt)
                
                st.success("Conteúdo Gerado com Sucesso!")
                
                st.markdown(
                    f"""
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; color: #333; font-family: sans-serif;">
                        {response.text}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                st.caption("👆 Copie o texto acima e cole na rede social.")
                
            except Exception as e:
                st.error(f"Erro: {e}")

    # --- RODAPÉ ---
    st.markdown("---")
    p, i = get_price_info(pais)
    st.markdown(f"<div style='text-align: center; color: gray;'>Licença ativa: {pais.split('(')[0]} • Plano: {p}</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="text-align: center; margin-top: 10px;">
        <a href="https://tally.so/r/w7e8a" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: bold;">Gerir Subscrição ➔</a>
    </div>
    """, unsafe_allow_html=True)
