import streamlit as st
import os
import psycopg2
import requests
from groq import Groq
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# --- 1. CONEXÃO COM O BANCO ---
def get_db_connection():
    return psycopg2.connect(
        host="db",
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

# --- 2. FUNÇÕES DE SINCRONIZAÇÃO DE MODELOS ---
def atualizar_modelos_groq():
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    try:
        modelos_groq = client.models.list()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM provedores WHERE nome = 'GROQ'")
        provedor_id = cur.fetchone()[0]
        
        for m in modelos_groq.data:
            cur.execute("""
                INSERT INTO modelos (provedor_id, modelo_id_api, nome_exibicao, ativo)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (provedor_id, modelo_id_api) 
                DO UPDATE SET ativo = True
            """, (provedor_id, m.id, m.id, True))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro Groq: {e}")
        return False

def atualizar_modelos_openrouter():
    url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id FROM provedores WHERE nome = 'OPENROUTER'")
            provedor_id = cur.fetchone()[0]
            
            for m in data:
                # Filtro para não lotar o banco com modelos irrelevantes
                if any(x in m['id'].lower() for x in ['llama', 'claude', 'gpt', 'mistral', 'gemini']):
                    cur.execute("""
                        INSERT INTO modelos (provedor_id, modelo_id_api, nome_exibicao, ativo)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (provedor_id, modelo_id_api) 
                        DO UPDATE SET nome_exibicao = EXCLUDED.nome_exibicao, ativo = True
                    """, (provedor_id, m['id'], m['name'], True))
            conn.commit()
            cur.close()
            conn.close()
            return True
        return False
    except Exception as e:
        st.error(f"Erro OpenRouter: {e}")
        return False

def atualizar_modelos_github():
    try:
        # IDs exatos aceitos pelo endpoint de inferência do GitHub
        modelos_github = [
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
            {"id": "Llama-3.3-70B-Instruct", "name": "Llama 3.3 70B"},
            {"id": "Phi-4", "name": "Phi-4"},
        ]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM provedores WHERE nome = 'GITHUB'")
        provedor_id = cur.fetchone()[0]
        
        for m in modelos_github:
            cur.execute("""
                INSERT INTO modelos (provedor_id, modelo_id_api, nome_exibicao, ativo)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (provedor_id, modelo_id_api) DO UPDATE SET ativo = True
            """, (provedor_id, m['id'], m['name'], True))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro GitHub: {e}")
        return False

# --- 3. FUNÇÃO DE CHAT UNIVERSAL ---
def chamar_ia(provedor_nome, modelo_api_id, mensagens, max_tokens, temperature):
    if provedor_nome == "GROQ":
        url = "https://api.groq.com/openai/v1/chat/completions"
        key = os.getenv("GROQ_API_KEY")
    elif provedor_nome == "OPENROUTER":
        url = "https://openrouter.ai/api/v1/chat/completions"
        key = os.getenv("OPENROUTER_API_KEY")
    elif provedor_nome == "GITHUB":
        url = "https://models.inference.ai.azure.com/chat/completions"
        key = os.getenv("GitHub_API_Key")
    
    headers = {
        "Authorization": f"Bearer {key}", 
        "Content-Type": "application/json"
    }
    
    if provedor_nome == "OPENROUTER":
        headers["HTTP-Referer"] = "http://localhost:8501"
        headers["X-Title"] = "AI Orchestrator"

    payload = {
        "model": modelo_api_id,
        "messages": mensagens,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Erro na API ({provedor_nome} {response.status_code}): {response.text}"
    except Exception as e:
        return f"Erro de conexão: {e}"

# --- 4. INTERFACE STREAMLIT ---
st.set_page_config(page_title="AI Orchestrator", layout="wide")
st.title("🤖 AI Orchestrator Multi-Provider")

# Sidebar: Configurações
st.sidebar.title("⚙️ Painel de Controle")

# 4.1 Seleção de Provedor e Modelo
try:
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, nome FROM provedores ORDER BY nome")
    lista_provedores = cur.fetchall()
    
    provedor_escolhido = st.sidebar.selectbox(
        "1. Escolha o Provedor", 
        options=lista_provedores, 
        format_func=lambda x: x[1]
    )

    cur.execute("SELECT id, modelo_id_api FROM modelos WHERE provedor_id = %s AND ativo = True ORDER BY modelo_id_api", (provedor_escolhido[0],))
    lista_modelos = cur.fetchall()

    modelo_escolhido = st.sidebar.selectbox(
        "2. Escolha o Modelo", 
        options=lista_modelos, 
        format_func=lambda x: x[1]
    )
    cur.close()
    conn.close()
except:
    st.sidebar.warning("Configure o banco e os provedores primeiro.")

# 4.2 Botão Sincronizar
if st.sidebar.button("🔄 Atualizar Catálogo"):
    with st.spinner("Sincronizando..."):
        if provedor_escolhido[1] == 'GROQ': sucesso = atualizar_modelos_groq()
        elif provedor_escolhido[1] == 'OPENROUTER': sucesso = atualizar_modelos_openrouter()
        elif provedor_escolhido[1] == 'GITHUB': sucesso = atualizar_modelos_github()
        
        if sucesso:
            st.sidebar.success("Catálogo Atualizado!")
            st.rerun()

st.sidebar.divider()

# 4.3 Sliders de Parâmetros
st.sidebar.subheader("🎛️ Parâmetros da Resposta")
max_tokens = st.sidebar.slider("Max Tokens", 64, 4096, 512, 64)
temperature = st.sidebar.slider("Temperature (Criatividade)", 0.0, 1.0, 0.7, 0.1)

# --- 5. ÁREA DE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir histórico da sessão
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do usuário
if prompt := st.chat_input("Digite sua mensagem..."):
    # Adicionar mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chamar IA
    with st.chat_message("assistant"):
        with st.spinner("IA processando..."):
            resposta = chamar_ia(
                provedor_escolhido[1], 
                modelo_escolhido[1], 
                [{"role": "user", "content": prompt}],
                max_tokens,
                temperature
            )
            st.markdown(resposta)
    
    st.session_state.messages.append({"role": "assistant", "content": resposta})

    # 6. SALVAMENTO NO BANCO (Com as novas colunas)
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO historico (modelo_id, nome_modelo, pergunta, resposta, max_tokens_used) 
            VALUES (%s, %s, %s, %s, %s)
            """,
            (modelo_escolhido[0], modelo_escolhido[1], prompt, resposta, max_tokens)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Erro ao salvar no banco: {e}")

# ... (abaixo do slider de temperature)

st.sidebar.divider()
st.sidebar.subheader("📜 Histórico Recente")

try:
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Busca as últimas 10 perguntas, ordenando pela data (mais nova primeiro)
    # Fazemos um JOIN para mostrar o nome amigável do modelo
    query = """
        SELECT h.pergunta, h.resposta, h.nome_modelo, h.data 
        FROM historico h 
        ORDER BY h.data DESC 
        LIMIT 10
    """
    cur.execute(query)
    rows = cur.fetchall()
    
    for row in rows:
        # Criamos um expansor para cada pergunta para não ocupar muito espaço na barra lateral
        # O título do expansor será a própria pergunta (cortada se for muito longa)
        titulo_pergunta = (row[0][:30] + '...') if len(row[0]) > 30 else row[0]
        with st.sidebar.expander(f"❓ {titulo_pergunta}"):
            st.caption(f"Modelo: {row[2]}")
            st.write(f"**P:** {row[0]}")
            st.write(f"**R:** {row[1]}")
            st.caption(f"Em: {row[3].strftime('%d/%m %H:%M')}")

    cur.close()
    conn.close()
except Exception as e:
    st.sidebar.error("Erro ao carregar mini-histórico.")