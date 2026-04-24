FROM python:3.11-slim

WORKDIR /app

# 系统依赖（Playwright 需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget gnupg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 浏览器（如果你启用 Playwright 抓取）
# RUN playwright install chromium --with-deps

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
