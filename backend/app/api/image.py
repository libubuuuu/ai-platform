"""功能3：图片画布 + 相似图生成。"""
from pydantic import BaseModel
from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.integrations.image.comfyui_client import (
    extract_prompt_from_image,
    generate_similar_images,
)

router = APIRouter(prefix="/api/image", tags=["image"])


class ExtractPromptRequest(BaseModel):
    image: str  # URL 或 base64


class GenerateRequest(BaseModel):
    prompt: str
    count: int = 4
    reference_image: str | None = None


@router.post("/extract_prompt")
async def extract_prompt(
    req: ExtractPromptRequest,
    user: dict = Depends(get_current_user),
):
    prompt = await extract_prompt_from_image(req.image)
    return {"prompt": prompt}


@router.post("/generate")
async def generate(
    req: GenerateRequest,
    user: dict = Depends(get_current_user),
):
    urls = await generate_similar_images(
        prompt=req.prompt,
        count=req.count,
        reference_image=req.reference_image,
    )
    return {"images": urls}
