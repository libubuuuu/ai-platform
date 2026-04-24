"""功能4：多账号矩阵 + 一键发布草稿箱。仅 admin 可用。"""
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_db
from app.core.security import require_admin
from app.integrations.publisher.sau_publisher import get_publisher
from app.models.content import RewrittenContent
from app.models.platform_account import PlatformAccount
from app.models.task import PublishTask
from app.models.user import User
from app.schemas.publish import (
    AccountCreateRequest,
    AccountOut,
    PublishRequest,
    PublishTaskOut,
)

router = APIRouter(prefix="/api/publish", tags=["publish", "admin-only"])


# ---------- 账号管理 ----------

@router.post("/accounts", response_model=AccountOut)
async def create_account(
    req: AccountCreateRequest,
    db: AsyncSessionLocal = Depends(get_db),
    admin: dict = Depends(require_admin),
):
    user_res = await db.execute(select(User).where(User.username == admin["username"]))
    u = user_res.scalar_one()
    acc = PlatformAccount(
        user_id=u.id,
        platform=req.platform,
        display_name=req.display_name,
        cookies=req.cookies,
        proxy_url=req.proxy_url,
        user_agent=req.user_agent,
    )
    db.add(acc)
    await db.commit()
    await db.refresh(acc)
    return acc


@router.get("/accounts", response_model=List[AccountOut])
async def list_accounts(
    db: AsyncSessionLocal = Depends(get_db),
    admin: dict = Depends(require_admin),
    platform: str | None = None,
):
    q = select(PlatformAccount)
    if platform:
        q = q.where(PlatformAccount.platform == platform)
    q = q.order_by(PlatformAccount.created_at.desc())
    result = await db.execute(q)
    return list(result.scalars().all())


@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: int,
    db: AsyncSessionLocal = Depends(get_db),
    admin: dict = Depends(require_admin),
):
    acc = await db.get(PlatformAccount, account_id)
    if not acc:
        raise HTTPException(404)
    await db.delete(acc)
    await db.commit()
    return {"ok": True}


# ---------- 发布任务 ----------

async def _run_publish_task(task_id: int):
    """后台任务：执行实际发布。"""
    async with AsyncSessionLocal() as db:
        task = await db.get(PublishTask, task_id)
        if not task:
            return
        task.status = "running"
        await db.commit()

        try:
            account = await db.get(PlatformAccount, task.account_id)
            content = await db.get(RewrittenContent, task.content_id)
            if not account or not content:
                raise RuntimeError("账号或内容不存在")

            publisher = get_publisher(account.platform)
            result = await publisher.publish_to_draft(
                account={
                    "id": account.id,
                    "platform": account.platform,
                    "cookies": account.cookies,
                    "storage_state": account.storage_state,
                    "proxy_url": account.proxy_url,
                    "user_agent": account.user_agent,
                },
                content={
                    "title": content.title,
                    "content_text": content.content_text,
                    "images": content.images,
                    "video_url": content.video_url,
                },
            )
            if result["success"]:
                task.status = "success"
                task.result = result
            else:
                task.status = "failed"
                task.error_message = result["message"]

        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)

        from datetime import datetime
        task.finished_at = datetime.utcnow()
        await db.commit()


@router.post("", response_model=List[PublishTaskOut])
async def publish(
    req: PublishRequest,
    bg: BackgroundTasks,
    db: AsyncSessionLocal = Depends(get_db),
    admin: dict = Depends(require_admin),
):
    # 强制 draft
    if req.target != "draft":
        raise HTTPException(400, "当前系统只允许发布到草稿箱（target=draft）")

    # 校验
    content = await db.get(RewrittenContent, req.rewritten_id)
    if not content:
        raise HTTPException(404, "洗稿内容不存在")

    user_res = await db.execute(select(User).where(User.username == admin["username"]))
    u = user_res.scalar_one()

    tasks: List[PublishTask] = []
    for acc_id in req.account_ids:
        acc = await db.get(PlatformAccount, acc_id)
        if not acc:
            continue
        t = PublishTask(
            user_id=u.id,
            content_id=content.id,
            account_id=acc.id,
            status="pending",
            target="draft",
        )
        db.add(t)
        tasks.append(t)
    await db.commit()
    for t in tasks:
        await db.refresh(t)
        bg.add_task(_run_publish_task, t.id)
    return tasks


@router.get("/tasks", response_model=List[PublishTaskOut])
async def list_tasks(
    db: AsyncSessionLocal = Depends(get_db),
    admin: dict = Depends(require_admin),
    limit: int = 50,
):
    result = await db.execute(
        select(PublishTask).order_by(PublishTask.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())
