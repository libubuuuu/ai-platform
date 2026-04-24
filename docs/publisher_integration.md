# 发布器接入指南

本系统的发布功能基于 [`dreammis/social-auto-upload`](https://github.com/dreammis/social-auto-upload)（SAU）。

骨架代码位于 `backend/app/integrations/publisher/sau_publisher.py`，
其中 `_publish_dispatch` 方法目前抛出 `NotImplementedError`，**这是有意的**——
为了避免在未充分测试的情况下意外发布到错误平台。

## 接入步骤

### 1. 拉取 SAU 子模块

```bash
git submodule update --init --recursive
```

完成后 `backend/vendor/social-auto-upload/` 应当出现完整代码。

### 2. 安装 SAU 依赖

```bash
cd backend/vendor/social-auto-upload
pip install -r requirements.txt
playwright install chromium
```

### 3. 为每个平台账号扫码登录生成 storage_state

SAU 每个平台 uploader 都提供 `setup` / `login` 函数。例如抖音：

```python
from uploader.douyin_uploader.main import douyin_setup
import asyncio

# 这一步会弹出浏览器，扫码登录
asyncio.run(douyin_setup(account_file="./cookies/douyin_account_a.json", handle=True))
```

把生成的 `cookies/*.json` 文件内容存到我们 `PlatformAccount.storage_state` 字段里。

### 4. 实现 `_publish_dispatch`

打开 `backend/app/integrations/publisher/sau_publisher.py`，在 `_publish_dispatch` 中按平台分支调用：

```python
async def _publish_dispatch(self, account, content):
    p = self.platform_name

    if p == "douyin":
        from uploader.douyin_uploader.main import DouYinVideo
        # 把账号的 storage_state 写到临时文件
        cookies_file = self._dump_cookies_to_tempfile(account)
        video = DouYinVideo(
            title=content["title"],
            file_path=content["video_url"],
            tags=[],
            publish_date=0,         # 0 = 立即发布；改成未来时间 = 定时发布
            account_file=cookies_file,
        )
        await video.main()         # ⚠️ SAU 默认会发布，需要修改/包装为只到草稿
        return {"draft_id": "n/a"}

    if p == "xiaohongshu":
        from uploader.xhs_uploader.main import XHSVideo
        # ... 类似实现

    raise NotImplementedError(f"{p}")
```

### 5. ⚠️ 关键：修改 SAU 让它停在草稿步骤

SAU 默认行为是直接点"发布"按钮。为了符合本系统"只发草稿箱"的安全底线，
你需要在每个平台的 uploader 里**注释掉点击发布按钮的那行**，
或者 fork 一份 SAU 自己改。

通用思路（以小红书为例）：
- 找到 `uploader/xhs_uploader/main.py` 中类似 `await page.click('button:has-text("发布")')` 的代码
- 改成 `await page.click('button:has-text("存草稿")')` 或者直接注释掉
- 提交 PR 回上游 / 维护自己的 fork

### 6. 测试

先用一个**测试账号**走全流程，看草稿箱是否正常生成。
**绝对不要用主账号做第一次测试。**

---

## 风控对抗清单

每个平台账号至少要做到：

- [ ] **独立代理 IP**：用 [proxy-cheap](https://proxy-cheap.com/)、芝麻代理等住宅代理
- [ ] **独立 storage_state**：不同账号用不同 cookies 文件
- [ ] **独立 User-Agent**：在 `PlatformAccount.user_agent` 字段配置
- [ ] **发布间隔随机化**：本系统已默认 30-120 秒延迟（`PUBLISH_MIN_DELAY_SEC`）
- [ ] **单账号每日发布上限**：建议 ≤ 3 篇（在你的业务层加限制）
- [ ] **避开平台敏感时段**：如发布检测严格的整点
- [ ] **草稿箱手动确认**：永远不要让程序点"发布"按钮

---

## 国外平台

### TikTok
SAU 已支持。同样按上面流程接入即可，但 TikTok 风控比国内严，强烈建议用住宅 IP + 长留 cookie。

### YouTube
推荐用 [YouTube Data API v3](https://developers.google.com/youtube/v3) 走官方上传，不要用浏览器自动化。
本骨架未集成，可参考 google-api-python-client。

### X (Twitter)
推荐用官方 [X API v2](https://developer.x.com/)（需要 Basic 套餐 $200/月）。
不建议浏览器自动化，X 反爬非常激进。
