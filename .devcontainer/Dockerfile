FROM python:3.11-slim
WORKDIR /app
COPY .devcontainer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .


#CMD ["streamlit", "run", "src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Streamlitのデフォルトポート（8501）を開放
EXPOSE 8501

#CMD ["streamlit", "run", "src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
