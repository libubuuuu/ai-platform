# AI Platform - 多平台内容智能运营系统

> 一站式自媒体内容发现、AI 改写、矩阵发布平台。  
> 双引擎架构：**MediaCrawler**（抓取）+ **social-auto-upload**（发布）。

---

## ⚠️ 首要安全提示（请先读）

1. **永远不要把 GitHub Token、API Key、账号密码发送给任何 AI 模型、聊天记录、截图**。  
   如果你不小心发过，立刻去对应平台撤销该凭据。
2. 本项目设计原则：**只发布到草稿箱，不直接自动发布**。这是保护你账号的底线。
3. 评论区投放功能**默认关闭自动执行**，仅生成文案建议，由你手动发送。
4. 管理员发布功能**锁死在 admin 账户**，需要修改 `.env` 中的密码才能使用。

---

## 🚀 5 大核心功能

| 编号 | 功能 | 实现状态 |
|---|---|---|
| 1 | 多平台热门/潜力/预爆内容监测（国内 7 平台 + 国外 3 平台） | ✅ 骨架 + 国内平台对接 |
| 2 | 内容购物车 + AI 洗稿复刻（文字/图片/视频） | ✅ 骨架 + Claude/DeepSeek 对接 |
| 3 | 图片画布 + AI 相似图生成（ComfyUI 对接） | ✅ 骨架 |
| 4 | 多账号矩阵 + 一键发布草稿箱（仅 admin） | ✅ 骨架 |
| 5 | 评论区 AI 文案生成（半自动，默认不自动发） | ✅ 骨架 |

**"骨架"的含义**：可跑、可点、数据流通、但平台细节需要你：
- 自己扫码登录各平台（Cookie 保存到数据库）
- 自己配 AI API Key（Claude / DeepSeek / 智谱）
- 自己部署 ComfyUI（图片生成功能才可用）
- 自己配代理 IP 池（多账号隔离才可用）

---

## 🏗️ 架构

```
┌────────────────────────────────────────────┐
│  前端：React 18 + Vite + Tailwind + Zustand │
└──────────────┬─────────────────────────────┘
               │  REST + SSE
┌──────────────▼─────────────────────────────┐
│  后端：FastAPI + SQLAlchemy + SQLite/PG    │
│  ┌──────────┬──────────┬────────┬────────┐ │
│  │ 抓取服务  │ 发布服务  │ AI服务  │ 图片服务 │ │
│  └────┬─────┴────┬─────┴───┬────┴───┬────┘ │
└───────┼──────────┼─────────┼────────┼──────┘
        ▼          ▼         ▼        ▼
   MediaCrawler social-auto Claude  ComfyUI
   (submodule)  -upload API    API
                (submodule)
```

---

## 📦 快速开始

### 1. 克隆仓库（含子模块）

```bash
git clone --recurse-submodules https://github.com/libubuuuu/ai-platform.git
cd ai-platform
```

如果你已经 clone 了但忘了 `--recurse-submodules`：
```bash
git submodule update --init --recursive
```

### 2. 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 复制并编辑配置
cp .env.example .env
# 打开 .env，至少配置 ADMIN_PASSWORD 和一个 AI 的 API Key

# 初始化数据库
python -m app.core.init_db

# 启动
uvicorn app.main:app --reload --port 8000
```

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173

### 4. Docker 一键启动（可选）

```bash
docker-compose up -d
```

---

## 🔐 管理员登录

默认账号：`admin`  
默认密码：在 `.env` 里的 `ADMIN_PASSWORD`（**第一次启动前必改！**）

只有 admin 能使用 **功能 4（一键发布）** 和 **功能 5（评论投放）**，普通用户只能用功能 1/2/3。

---

## 🔗 子模块说明

本项目通过 git submodule 引用两个上游项目：

| 子模块路径 | 上游项目 | 用途 |
|---|---|---|
| `backend/vendor/MediaCrawler` | [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) | 多平台内容抓取 |
| `backend/vendor/social-auto-upload` | [dreammis/social-auto-upload](https://github.com/dreammis/social-auto-upload) | 多平台草稿箱发布 |

**更新子模块到上游最新版**：
```bash
git submodule update --remote --merge
git add backend/vendor/*
git commit -m "chore: update vendor submodules"
```

---

## 📋 已支持平台

### 抓取（功能 1）
- ✅ 小红书、抖音、快手、B站、微博、贴吧、知乎（通过 MediaCrawler）
- ⚠️ X / YouTube / TikTok：建议使用官方 API，见 `docs/international.md`

### 发布（功能 4）
- ✅ 抖音、小红书、视频号、快手、B站、百家号、TikTok（通过 social-auto-upload）
- 所有发布默认走**草稿箱**，不直接公开

---

## ⚖️ 免责声明

本项目仅用于学习研究。使用者应：
- 遵守各平台服务协议与 robots.txt
- 遵守《网络安全法》等法律法规
- 不得用于刷量、恶意爬取、骚扰他人
- 对账号被风控/封禁承担全部责任

本项目开发者不对任何因使用本项目导致的损失负责。

---

## 📄 License

MIT
