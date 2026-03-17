# Chat IA Multi-Container com Persistência (PostgreSQL + Docker Compose)

# 🤖 AI Orchestrator Multi-Provider

Este é um orquestrador de Inteligência Artificial robusto, desenvolvido com **Python**, **Streamlit** e **PostgreSQL**. O projeto permite gerenciar múltiplos provedores de LLM (Groq, OpenRouter e GitHub Models) em uma única interface, com controle total sobre parâmetros de resposta e persistência de histórico.

## 🚀 Funcionalidades

- **Multi-Provedor:** Integração nativa com Groq, OpenRouter e GitHub Models.
- **Gestão de Catálogo Dinâmica:** Sincronização automática de modelos disponíveis via API, salvando-os no banco de dados.
- **Parâmetros Personalizáveis:** Controle de `Max Tokens` e `Temperature` via interface (Sidebar).
- **Histórico Persistente:** Armazenamento de todas as interações no PostgreSQL, incluindo metadados do modelo utilizado.
- **Interface Intuitiva:** Chat moderno com histórico rápido e expansível na barra lateral.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** [Python 3.9+](https://www.python.org/)
- **Frontend/Interface:** [Streamlit](https://streamlit.io/)
- **Banco de Dados:** [PostgreSQL](https://www.postgresql.org/)
- **Containerização:** [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- **Bibliotecas Principais:** `psycopg2-binary`, `requests`, `python-dotenv`, `groq`.

## 📦 Como Instalar e Rodar

### Pré-requisitos

- Docker Desktop instalado.

### 1. Clone o repositório:

```bash
git clone git@github.com:BrunoKaram/ai-chat-docker-orchestration.git
cd ai-chat-docker-orchestration
```

### 2. Configure as variáveis de ambiente:

Crie um arquivo .env na raiz do projeto e preencha com suas credenciais:

POSTGRES_DB=ai_orchestrator
POSTGRES_USER=postgres
POSTGRES_PASSWORD=suasenha
GROQ_API_KEY=sua_chave_groq
OPENROUTER_API_KEY=sua_chave_openrouter
GitHub_API_Key=sua_chave_github

### 3. Suba os containers:

Bash
docker-compose up -d

Inicie o serviço do Streamlit:
Bash
docker exec -it app-ia streamlit run app.py
Acesse as interfaces:

Aplicação Chat IA: http://localhost:8501

Gerenciador de Banco (Adminer): http://localhost:8080

### 3. 🗄️ Estrutura do Banco de Dados

O projeto utiliza um esquema relacional para garantir a integridade dos logs e do catálogo.
Execute o script abaixo no seu cliente SQL (como o Adminer em localhost:8080):

-- 1. Tabela de Provedores
CREATE TABLE IF NOT EXISTS provedores (
id SERIAL PRIMARY KEY,
nome VARCHAR(50) UNIQUE NOT NULL
);

-- 2. Tabela de Modelos
CREATE TABLE IF NOT EXISTS modelos (
id SERIAL PRIMARY KEY,
provedor_id INTEGER REFERENCES provedores(id) ON DELETE CASCADE,
modelo_id_api VARCHAR(100) NOT NULL,
nome_exibicao VARCHAR(100),
ativo BOOLEAN DEFAULT TRUE,
UNIQUE(provedor_id, modelo_id_api)
);

-- 3. Tabela de Histórico
CREATE TABLE IF NOT EXISTS historico (
id SERIAL PRIMARY KEY,
modelo_id INTEGER REFERENCES modelos(id) ON DELETE SET NULL,
nome_modelo VARCHAR(100),
pergunta TEXT NOT NULL,
resposta TEXT NOT NULL,
max_tokens_used INTEGER,
data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserção inicial
INSERT INTO provedores (nome) VALUES ('GROQ'), ('OPENROUTER'), ('GITHUB')
ON CONFLICT DO NOTHING;
