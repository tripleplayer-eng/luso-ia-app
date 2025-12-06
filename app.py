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
    /* Botão de gerar vibrante */
    .stButton button { 
        width: 100%; 
        border-radius: 12px; 
        font-weight: bold; 
        background: linear-gradient(to right, #2563eb, #4f46e5); 
        color: white; 
        padding: 0.7rem 1rem;
        border: none;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
        transition: all 0.3s ease;
    }
    .stButton button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
    }
    /* Legenda mais bonita */
    .caption-text {
        text-align: center;
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 20px;
    }
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
        # FRASE DE CHAMADA À AÇÃO (CTA) MELHORADA
        st.markdown('<p class="caption-text">🚀 Transforme ideias simples em posts virais em segundos.</p>', unsafe_allow_html=True)

    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        modelo_ativo = get_working_model()
    except:
        st.error("Erro Crítico: API Key em falta.")
        st.stop()

    # --- 1. SELETOR DE REDE ---
    st.write("### 1. Onde vai publicar?")
    
    rede_selecionada = image_select(
        label="",
        images=[
            "https://cdn-icons-png.flaticon.com/512/2111/2111463.png", # Instagram
            "https://cdn-icons-png.flaticon.com/512/733/733585.png",   # WhatsApp
            "https://cdn-icons-png.flaticon.com/512/174/174857.png",   # LinkedIn
            "https://cdn-icons-png.flaticon.com/512/1384/1384060.png", # YouTube
            "https://cdn-icons-png.flaticon.com/512/3046/3046121.png", # TikTok
            "https://cdn-icons-png.flaticon.com/512/5968/5968764.png", # Facebook
            "https://cdn-icons-png.flaticon.com/512/5969/5969020.png", # X
            "https://cdn-icons-png.flaticon.com/512/4922/4922073.png", # Blog
        ],
        captions=["Instagram", "WhatsApp", "LinkedIn", "YouTube", "TikTok", "Facebook", "X / Twitter", "Blog"],
        index=0,
        use_container_width=False
    )

    # --- 2. FORMULÁRIO ---
    st.markdown("---")
    with st.form("gerador"):
        st.write("### 2. Detalhes")
        col_a, col_b = st.columns(2)
        with col_a:
            # LISTA DE PAÍSES COM BANDEIRAS
            pais = st.selectbox("País Alvo", 
                [
                    "🇵🇹 Portugal (PT-PT)", 
                    "🇧🇷 Brasil (PT-BR)", 
                    "🇦🇴 Angola (PT-AO)", 
                    "🇲🇿 Moçambique (PT-MZ)", 
                    "🇨🇻 Cabo Verde (PT-CV)", 
                    "🇬🇼 Guiné-Bissau (PT-GW)", 
                    "🇸🇹 São Tomé e Príncipe (PT-ST)", 
                    "🇹🇱 Timor-Leste (PT-TL)"
                ]
            )
        with col_b:
            tom = st.selectbox("Tom", ["Profissional", "Divertido", "Vendas/Promoção", "Storytelling", "Institucional"])
            
        negocio = st.text_input("O seu Negócio:", placeholder="Ex: Clínica Dentária, Loja de Roupa...")
        tema = st.text_area("Tópico do Conteúdo:", placeholder="Ex: Promoção de Natal ou Dicas de Prevenção")
        
        btn = st.form_submit_button("✨ Gerar Conteúdo Mágico", type="primary")

    # --- 3. RESULTADO ---
    if btn and negocio:
        rede_nome = "Rede Social"
        if "2111463" in rede_selecionada: rede_nome = "Instagram"
        elif "733585" in rede_selecionada: rede_nome = "WhatsApp"
        elif "174857" in rede_selecionada: rede_nome = "LinkedIn"
        elif "1384060" in rede_selecionada: rede_nome = "YouTube Shorts"
        elif "3046121" in rede_selecionada: rede_nome = "TikTok"
        elif "5968764" in rede_selecionada: rede_nome = "Facebook"
        elif "5969020" in rede_selecionada: rede_nome = "X (Twitter)"
        else: rede_nome = "Blog Post"

        with st.spinner(f"A criar para {rede_nome} em {pais}..."):
            
            prompt = f"""
            Atua como Copywriter Sénior. Modelo: {modelo_ativo}.
            
            CONTEXTO:
            - País: {pais}
            - Negócio: {negocio}
            - Rede: {rede_nome}
            - Tom: {tom}
            - Tópico: {tema}
            
            REGRAS ESPECÍFICAS ({rede_nome}):
            - Instagram: Visual, emojis, quebras de linha, hashtags no fim.
            - WhatsApp: Curto, direto, estilo "mensagem para lista de transmissão".
            - TikTok/YouTube: CRIA UM GUIÃO DE VÍDEO (Cena 1, Cena 2, Texto Falado).
            - LinkedIn: Profissional, autoridade, parágrafos curtos.
            - Blog: Estrutura SEO (H1, H2, Conclusão).
            
            CULTURA: Usa a moeda e gírias de {pais}.
            """
            
            try:
                model = genai.GenerativeModel(modelo_ativo)
                response = model.generate_content(prompt)
                
                st.success("Conteúdo Gerado com Sucesso!")
                st.markdown(f"**Formato:** {rede_nome} • **Mercado:** {pais}")
                
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
    # Limpeza visual da string do país para o rodapé (tirar a bandeira e o código)
    pais_limpo = pais.split('(')[0].replace('🇵🇹','').replace('🇧🇷','').replace('🇦🇴','').replace('🇲🇿','').replace('🇨🇻','').replace('🇬🇼','').replace('🇸🇹','').replace('🇹🇱','').strip()
    
    st.markdown(f"<div style='text-align: center; color: gray;'>Licença ativa: {pais_limpo} • Plano: {p}</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="text-align: center; margin-top: 10px;">
        <a href="https://tally.so/r/81qLVx" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: bold;">Gerir Subscrição ➔</a>
    </div>
    """, unsafe_allow_html=True)

