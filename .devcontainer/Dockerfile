FROM python:3.11-slim
WORKDIR /app
COPY .devcontainer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

#Gitのインストール
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  git \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Gitにとって安全なディレクトリに設定
RUN git config --global --add safe.directory /app

# GitHubの秘密鍵を作成すること
COPY .ssh/ /root/.ssh/
RUN chmod 700 /root/.ssh && \
    chmod 600 /root/.ssh/id_rsa && \
    chmod 644 /root/.ssh/id_rsa.pub

# Streamlitのデフォルトポート（8501）を開放
EXPOSE 8501
