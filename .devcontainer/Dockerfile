# ベース
FROM python:3.11-slim AS base
WORKDIR /app
COPY .devcontainer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Streamlitのデフォルトポート（8501）を開放
EXPOSE 8501

# 本番用ステージ
FROM base AS production
COPY . .

# 開発用ステージ
FROM base AS development
#Gitのインストール
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  git \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Gitにとって安全なディレクトリに設定
RUN git config --global --add safe.directory /app
COPY . .