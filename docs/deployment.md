# 部署清单（First-time Setup Checklist）

按这个顺序做，第一次跑通需要约 1-2 小时。

## ☑️ 第 1 步：克隆仓库 + 子模块

```bash
git clone --recurse-submodules https://github.com/libubuuuu/ai-platform.git
cd ai-platform
```

如果忘了 `--recurse-submodules`：
```bash
git submodule update --init --recursive
```

## ☑️ 第 2 步：后端基础

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

**编辑 `.env`，至少配置：**
- `SECRET_KEY` - 用 `python -c "import secrets; print(secrets.token_urlsafe(32))"` 生成
- `ADMIN_PASSWORD` - 你的管理员密码（≥6 位）
- `OPENAI_API_KEY` 或 `ANTHROPIC_API_KEY` - AI 服务密钥（至少一个）

```bash
python -m app.core.init_db
uvicorn app.main:app --reload --port 8000
```

打开 http://localhost:8000/docs 应该能看到 API 文档。

## ☑️ 第 3 步：前端

```bash
cd ../frontend
npm install
npm run dev
```

打开 http://localhost:5173，用 admin / 你设置的密码登录。

## ☑️ 第 4 步：MediaCrawler 登录平台

抓取功能需要每个平台先扫码登录。

```bash
cd backend/vendor/MediaCrawler
pip install -r requirements.txt
playwright install

# 小红书
python main.py --platform xhs --type search --keywords "测试" --pages 1
# （首次会弹出二维码，扫码登录后 cookie 会缓存到 browser_data/）

# 抖音
python main.py --platform dy --type search --keywords "测试" --pages 1

# 其他平台同理：bili / ks / wb / tieba / zhihu
```

登录一次后，本系统就能通过 MediaCrawler 抓取了。

## ☑️ 第 5 步（可选）：ComfyUI 图片生成

只在你要用功能 3（图片画布）时才需要。

1. 部署 ComfyUI: https://github.com/comfyanonymous/ComfyUI
2. 在 `.env` 中：
   ```
   COMFYUI_BASE_URL="http://127.0.0.1:8188"
   COMFYUI_ENABLED=true
   ```
3. 重启后端

## ☑️ 第 6 步（仅 admin）：发布功能接入

详见 [`publisher_integration.md`](./publisher_integration.md)。

**强烈建议先用测试账号跑一遍。**

## ☑️ 第 7 步（推荐）：代理 IP 池

每个平台账号配独立代理，在前端"账号管理"页填 `proxy_url`。
格式：`http://user:pass@host:port`

推荐住宅代理服务（按需选择，本项目不背书任何特定供应商）。

---

## 常见问题

### 1. 启动后访问 localhost:5173 显示空白

检查浏览器 Console。一般是后端没启动或者 CORS_ORIGINS 配错。

### 2. MediaCrawler 报错 "未登录"

去 `backend/vendor/MediaCrawler/browser_data/` 看 cookie 文件是否存在。
不存在就重新走第 4 步扫码。

### 3. 洗稿失败 "未配置 OPENAI_API_KEY"

在 `.env` 配置至少一个 AI 服务的 key。DeepSeek 最便宜，用法：
```
OPENAI_API_KEY="sk-xxx"
OPENAI_BASE_URL="https://api.deepseek.com"
OPENAI_MODEL="deepseek-chat"
DEFAULT_AI_PROVIDER="openai"
```

### 4. 想换数据库到 PostgreSQL

```
DATABASE_URL="postgresql+asyncpg://user:pass@localhost/ai_platform"
```
然后 `pip install asyncpg`，重启即可。

### 5. 一键发布报 NotImplementedError

这是有意的安全设计。请按 [publisher_integration.md](./publisher_integration.md) 第 4 步实现具体平台分支。
