# Chat IA Multi-Container com Persistência (PostgreSQL + Docker Compose)

Este projeto é uma aplicação Full-Stack containerizada que utiliza Inteligência Artificial (LLM via Groq API) para responder perguntas dos usuários, armazenando todo o histórico de conversas em um banco de dados relacional PostgreSQL.

## 🚀 Tecnologias Utilizadas

- **Python 3.12**: Linguagem base da aplicação.
- **Streamlit**: Interface web moderna e interativa.
- **Docker & Docker Compose**: Orquestração de containers para App, Banco de Dados e Gerenciador de Banco.
- **PostgreSQL 15**: Banco de Dados relacional para persistência do histórico.
- **Groq Cloud API**: Processamento de IA ultra-rápido (Llama 3.1).
- **Adminer**: Interface web para administração do banco de dados.

## 🏗️ Arquitetura do Projeto

O projeto é composto por três serviços principais que se comunicam em uma rede isolada do Docker:

1.  **app-ia**: Container Python que roda a interface Streamlit.
2.  **db-postgres**: Banco de dados para armazenamento persistente.
3.  **db-adminer**: Ferramenta gráfica para visualizar e gerenciar as tabelas do banco.

## 🛠️ Como Executar o Projeto

### Pré-requisitos

- Docker Desktop instalado.
- Uma chave de API da [Groq Cloud](https://console.groq.com/).

### Passo a Passo

1. **Clone o repositório:**

   ```bash
   git clone git@github.com:BrunoKaram/projeto-3.git
   cd projeto-3
   ```

2. **Configure as variáveis de ambiente:**

Crie um arquivo .env na raiz do projeto e preencha com suas credenciais:

Snippet de código
GROQ_API_KEY=gsk_sua_chave_aqui
POSTGRES_USER=bruno
POSTGRES_PASSWORD=sua_senha_aqui
POSTGRES_DB=ia_database
Suba os containers:

Bash
docker-compose up -d
Inicie o serviço do Streamlit:

Bash
docker exec -it app-ia streamlit run app.py
Acesse as interfaces:

Aplicação Chat IA: http://localhost:8501

Gerenciador de Banco (Adminer): http://localhost:8080

3. **Estrutura do Banco de Dados:**
   A aplicação cria automaticamente a tabela historico com a seguinte estrutura:

id: Chave primária serial.

pergunta: Texto enviado pelo usuário.

resposta: Resposta gerada pela IA.

data: Timestamp da interação.

Desenvolvido por Bruno Karam como parte da jornada de estudos DevOps.

---
