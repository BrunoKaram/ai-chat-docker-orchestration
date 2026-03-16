FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
# Adicionamos o streamlit aqui
RUN pip install --no-cache-dir groq python-dotenv streamlit psycopg2-binary

# O Streamlit usa a porta 8501 por padrão
EXPOSE 8501

CMD ["sleep", "infinity"]