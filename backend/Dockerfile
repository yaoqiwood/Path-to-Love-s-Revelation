# ============================================
# Backend Dockerfile - FastAPI + Celery
# ============================================
FROM python:3.12-slim AS base

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 创建必要目录
RUN mkdir -p storage logs export

# 暴露端口
EXPOSE 8011

# 默认启动 FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8011", "--workers", "4"]
