"""相似图片生成：对接本地 ComfyUI。

流程：
1. 用户上传一张参考图到画布
2. 前端调用 /api/image/extract_prompt，我们用视觉模型抽取图的描述词
3. 用户确认或编辑描述词后，调用 /api/image/generate
4. 我们提交 workflow 到 ComfyUI，返回生成的图 URL

⚠️ 骨架说明：
- 本文件只有最小接入逻辑
- 你需要自己部署 ComfyUI 并在 .env 里设置 COMFYUI_ENABLED=true
- workflow JSON 需要按你的 ComfyUI 节点定制（这里给个通用 SDXL 模板示意）
"""
from typing import Optional
import uuid
import httpx
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


async def extract_prompt_from_image(image_url_or_base64: str) -> str:
    """用视觉 LLM 抽取图片描述词。

    实现思路：调用 Claude / GPT-4o 的 Vision 能力。
    这里给一个最小实现，实际可以调得更细（色调、构图、风格标签）。
    """
    # 骨架：返回占位。真接入时按 provider 调 Vision API。
    logger.info("extract_prompt_from_image: 骨架实现，返回占位")
    return "a photo, highly detailed, cinematic lighting, 4k"


async def generate_similar_images(
    prompt: str,
    count: int = 4,
    reference_image: Optional[str] = None,
) -> list[str]:
    """向 ComfyUI 提交生成任务。

    返回生成图片的 URL 列表。
    """
    if not settings.COMFYUI_ENABLED:
        raise RuntimeError(
            "ComfyUI 未启用。请：\n"
            "1. 在本地部署 ComfyUI（https://github.com/comfyanonymous/ComfyUI）\n"
            "2. 在 .env 中设置 COMFYUI_ENABLED=true 和正确的 COMFYUI_BASE_URL"
        )

    # 这里给出最简单的 prompt 调用框架，真实使用请替换成你自己导出的 workflow JSON
    client_id = str(uuid.uuid4())
    workflow = _build_simple_workflow(prompt, count)

    async with httpx.AsyncClient(timeout=180) as client:
        # 提交任务
        resp = await client.post(
            f"{settings.COMFYUI_BASE_URL}/prompt",
            json={"prompt": workflow, "client_id": client_id},
        )
        resp.raise_for_status()
        prompt_id = resp.json().get("prompt_id")

        # 轮询结果
        for _ in range(60):  # 最多等 60 次 * 3s = 3 分钟
            history_resp = await client.get(
                f"{settings.COMFYUI_BASE_URL}/history/{prompt_id}"
            )
            history = history_resp.json()
            if prompt_id in history:
                outputs = history[prompt_id].get("outputs", {})
                image_urls = []
                for node_output in outputs.values():
                    for img in node_output.get("images", []):
                        url = (
                            f"{settings.COMFYUI_BASE_URL}/view"
                            f"?filename={img['filename']}"
                            f"&subfolder={img.get('subfolder','')}"
                            f"&type={img.get('type','output')}"
                        )
                        image_urls.append(url)
                return image_urls
            import asyncio
            await asyncio.sleep(3)

    raise TimeoutError("ComfyUI 生成超时")


def _build_simple_workflow(prompt: str, batch_size: int) -> dict:
    """构造最小 SDXL workflow。

    真实使用：
    1. 在 ComfyUI 界面拖好 workflow
    2. 点"Save (API Format)" 导出 JSON
    3. 替换这个函数的返回值
    """
    # 这里留空 workflow 示例，真接入时填充
    return {
        "3": {
            "inputs": {"seed": 0, "steps": 20, "cfg": 7, "sampler_name": "euler",
                       "scheduler": "normal", "denoise": 1,
                       "model": ["4", 0], "positive": ["6", 0],
                       "negative": ["7", 0], "latent_image": ["5", 0]},
            "class_type": "KSampler",
        },
        "4": {"inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
              "class_type": "CheckpointLoaderSimple"},
        "5": {"inputs": {"width": 1024, "height": 1024, "batch_size": batch_size},
              "class_type": "EmptyLatentImage"},
        "6": {"inputs": {"text": prompt, "clip": ["4", 1]},
              "class_type": "CLIPTextEncode"},
        "7": {"inputs": {"text": "worst quality, low quality", "clip": ["4", 1]},
              "class_type": "CLIPTextEncode"},
        "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]},
              "class_type": "VAEDecode"},
        "9": {"inputs": {"filename_prefix": "aiplatform", "images": ["8", 0]},
              "class_type": "SaveImage"},
    }
