"""
Google 翻译工具
用作 DeepL 翻译失败时的保底方案
"""

from typing import List, Union, Optional
from googletrans import Translator, LANGUAGES

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def translate(
    text: Union[str, List[str]],
    target_lang: str,
    source_lang: Optional[str] = None,
    proxy: Optional[str] = None,
) -> Union[str, List[str]]:
    """
    使用 Google 翻译

    :param text: 要翻译的文本或文本列表
    :param target_lang: 目标语言代码（如 'zh-cn', 'en', 'ja'）
    :param source_lang: 源语言代码（可选，默认自动检测）
    :param proxy: 代理地址（可选，优先使用此参数，其次使用环境变量）
    :return: 翻译结果
    """
    # 验证目标语言
    target_lang_lower = target_lang.lower()
    if target_lang_lower not in LANGUAGES:
        raise ValueError(f"Google Translate 不支持语言: {target_lang_lower}")

    # 确定代理
    proxy_url = proxy or settings.LOCAL_HTTP_PROXY

    try:
        translator = Translator(proxy=proxy_url)

        # 执行翻译
        result = await translator.translate(
            text,
            dest=target_lang_lower,
            # src=source_lang.lower() if source_lang else "auto",
        )

        # 返回结果
        if isinstance(text, str):
            return result.text
        else:
            return [r.text for r in result]

    except Exception as e:
        logger.error(f"Google 翻译失败: {str(e)}")
        raise


async def detect_language(text: str, proxy: Optional[str] = None) -> str:
    """
    检测文本语言

    :param text: 要检测的文本
    :param proxy: 代理地址（可选）
    :return: 语言代码（如 'en', 'zh-cn'）
    """
    proxy_url = proxy or settings.LOCAL_HTTP_PROXY

    try:
        translator = Translator(proxy=proxy_url)
        result = await translator.detect(text)

        # 只有当置信度 > 0.5 时返回检测结果
        if result.confidence > 0.5:
            logger.debug(
                f"Detected language: {result.lang} (confidence: {result.confidence})"
            )
            return result.lang
        else:
            logger.warning(
                f"Low confidence language detection: {result.lang} ({result.confidence})"
            )
            return "unknown"

    except Exception as e:
        logger.error(f"语言检测失败: {str(e)}")
        return "unknown"


# 导出函数
__all__ = ["translate", "detect_language"]
