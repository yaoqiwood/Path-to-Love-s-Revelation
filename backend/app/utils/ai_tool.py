#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2026/3/11 17:17
# @File           : ai_tool.py
# @IDE            : PyCharm
# @desc           :
import os
from typing import Optional
from app.core.config import settings
import base64

def get_proxies() -> Optional[dict]:
    """获取代理配置"""
    if settings.LOCAL_HTTP_PROXY:
        return {
            "http": settings.LOCAL_HTTP_PROXY,
            "https": settings.LOCAL_HTTP_PROXY,
        }
    return None


def image_to_data_uri(image_path: str) -> str:
    """将本地图片文件转为 base64 data URI"""
    ext = os.path.splitext(image_path)[1].lower().lstrip(".")
    mime_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "bmp": "image/bmp",
    }
    mime_type = mime_map.get(ext, "image/jpeg")

    with open(image_path, "rb") as f:
        image_data = f.read()

    b64_str = base64.b64encode(image_data).decode("utf-8")
    return f"data:{mime_type};base64,{b64_str}"


def image_to_base64(image_path: str) -> tuple[str, str]:
    """将本地图片文件转为 (mime_type, base64_data) 元组，
    可直接用于 Gemini inlineData 等场景，避免 data URI 往返开销。
    """
    ext = os.path.splitext(image_path)[1].lower().lstrip(".")
    mime_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "bmp": "image/bmp",
    }
    mime_type = mime_map.get(ext, "image/jpeg")

    with open(image_path, "rb") as f:
        image_data = f.read()

    b64_str = base64.b64encode(image_data).decode("utf-8")
    return mime_type, b64_str


def get_headers(api_key) -> dict:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }