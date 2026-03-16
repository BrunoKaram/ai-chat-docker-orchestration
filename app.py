import streamlit as st
from groq import Groq
import os
import psycopg2 # A biblioteca que acabamos de instalar
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
def get_db_connection():
    # O host continua sendo "db" (nome do serviço no compose)
    conn = psycopg2.connect(
        host="db",
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    return conn

# Criar a tabela se não existir
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id SERIAL PRIMARY KEY,
            pergunta TEXT,
            resposta TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Inicializa o banco ao rodar o app
init_db()

# --- INTERFACE STREAMLIT ---
st.title("Chat IA com Memória (Postgres)")

# --- CARREGAR HISTÓRICO DO BANCO ---
st.subheader("Histórico de Conversas Salvas")
try:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT pergunta, resposta, data FROM historico ORDER BY data DESC LIMIT 5")
    rows = cur.fetchall()
    for row in rows:
        with st.expander(f"Pergunta em: {row[2].strftime('%d/%m %H:%M')}"):
            st.write(f"**Você:** {row[0]}")
            st.write(f"**IA:** {row[1]}")
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Erro ao carregar histórico: {e}")

st.divider()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("O que deseja saber?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chamada da IA
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    
    full_response = response.choices[0].message.content
    
    with st.chat_message("assistant"):
        st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # --- SALVANDO NO POSTGRES ---
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO historico (pergunta, resposta) VALUES (%s, %s)",
            (prompt, full_response)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Erro ao salvar no banco: {e}")