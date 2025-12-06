import streamlit as st
import google.generativeai as genai

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Luso-IA App", page_icon="🇵🇹", layout="centered")

# --- CSS PERSONALIZADO (Para os Ícones das Redes) ---
st.markdown("""
<style>
    /* Estilo dos Botões de Rede Social */
    div[role="radiogroup"] > label > div:first-of-type {
        display: none; /* Esconde a bolinha do rádio */
    }
    div[role="radiogroup"] {
        gap: 12px;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
    }
    div[role="radiogroup"] label {
        background-color: #ffffff;
        padding: 15px 25px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        flex-grow: 1;
        min-width: 100px;
    }
    div[role="radiogroup"] label:hover {
        border-color: #2563eb;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(37, 99, 235, 0.15);
    }
    /* Quando selecionado */
    div[role="radiogroup"] label[data-checked="true"] {
        background-color: #2563eb !important;
        color: white !important;
        border-color: #2563eb;
        font-weight: bold;
    }
    div[role="radiogroup"] label[data-checked="true"] p {
        color: white !important;
    }
    
    /* Ajuste de Texto */
    .big-font { font-size: 20px !important; }
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
        st.caption("Selecione a rede e crie conteúdo.")

    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        modelo_ativo = get_working_model()
    except:
        st.error("Erro Crítico: API Key em falta.")
        st.stop()

    # --- 1. SELETOR DE REDE (VISUAL) ---
    st.write("### 1. Onde vai publicar?")
    
    # Usamos emojis grandes como ícones visuais
    rede_selecionada = st.radio(
        "Escolha a rede:",
        [
            "🟣 Instagram", 
            "🔵 Facebook", 
            "💼 LinkedIn", 
            "⚫ TikTok", 
            "🔴 YouTube",
            "🟢 WhatsApp", 
            "🐦 Twitter / X", 
            "📝 Blog SEO"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

    # --- 2. FORMULÁRIO ---
    st.markdown("---")
    with st.form("gerador"):
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
        with st.spinner(f"A criar para {rede_selecionada} em {pais}..."):
            
            prompt = f"""
            Atua como Copywriter Sénior. Modelo: {modelo_ativo}.
            
            CONTEXTO:
            - País: {pais}
            - Negócio: {negocio}
            - Rede: {rede_selecionada}
            - Tom: {tom}
            - Tópico: {tema}
            
            REGRAS ESPECÍFICAS PARA {rede_selecionada}:
            - Instagram (🟣): Visual, emojis, quebras de linha, hashtags no fim.
            - LinkedIn (💼): Profissional, foco em carreira/negócio, parágrafos curtos.
            - Facebook (🔵): Comunitário, perguntas para engajamento.
            - TikTok/YouTube (⚫/🔴): GERA UM GUIÃO DE VÍDEO (Cena 1, Cena 2, Fala).
            - WhatsApp (🟢): Curto, direto, "Olá [Nome]", chamada para ação.
            - Blog (📝): Título H1, introdução, pontos chave, conclusão SEO.
            
            CULTURA: Usa a moeda e gírias de {pais}.
            """
            
            try:
                model = genai.GenerativeModel(modelo_ativo)
                response = model.generate_content(prompt)
                
                st.success("Conteúdo Gerado com Sucesso!")
                st.markdown(f"### Pré-visualização ({rede_selecionada})")
                
                # Caixa de texto bonita
                st.markdown(
                    f"""
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; color: #333;">
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
    
    # O TEU LINK DO TALLY NO FIM
    st.markdown(f"""
    <div style="text-align: center; margin-top: 10px;">
        <a href="https://tally.so/r/w7e8a" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: bold;">Gerir Subscrição ➔</a>
    </div>
    """, unsafe_allow_html=True)







