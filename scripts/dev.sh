#!/usr/bin/env bash
# 一键启动脚本（开发模式）
# 用法：bash scripts/dev.sh

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔧 检查子模块..."
cd "$ROOT"
git submodule update --init --recursive || echo "⚠️  子模块未配置远程，跳过"

echo "🐍 启动后端..."
cd "$ROOT/backend"
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "⚠️  已生成 .env，请编辑后再次运行（必须设置 SECRET_KEY 和 ADMIN_PASSWORD）"
  exit 1
fi

python -m app.core.init_db

uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "⚛️  启动前端..."
cd "$ROOT/frontend"
if [ ! -d "node_modules" ]; then
  npm install
fi
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
