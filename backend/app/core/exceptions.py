"""
全局异常处理器
自动捕获所有未处理异常并发送飞书告警
"""

from enum import Enum
from typing import Optional

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.utils.feishu import send_alert
from app.core.config import settings

logger = get_logger(__name__)


# ==================== 业务错误码 ====================


class BizError(str, Enum):
    """业务错误码枚举"""

    # 认证相关
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"  # 凭据无效
    USER_DOES_NOT_EXIST = "USER_DOES_NOT_EXIST"  # 用户不存在
    PASSWORD_ERROR = "PASSWORD_ERROR"  # 密码错误
    USER_DISABLED = "USER_DISABLED"  # 用户已禁用
    PERMISSION_DENIED = "PERMISSION_DENIED"  # 权限不足

    # 通用
    NOT_FOUND = "NOT_FOUND"  # 资源不存在
    ALREADY_EXISTS = "ALREADY_EXISTS"  # 资源已存在
    VALIDATION_ERROR = "VALIDATION_ERROR"  # 参数验证失败
    BAD_REQUEST = "BAD_REQUEST"  # 请求错误
    INTERNAL_ERROR = "INTERNAL_ERROR"  # 服务器内部错误


# ==================== 业务异常 ====================


class BizException(StarletteHTTPException):
    """带业务错误码的异常

    响应体:
        {"code": "TOKEN_EXPIRED", "message": "登录已过期", "status_code": 401}
    """

    def __init__(
        self,
        code: BizError,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: Optional[list] = None,
        headers: Optional[dict] = None,
    ):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(status_code=status_code, detail=message, headers=headers)


# ==================== 异常处理器 ====================


async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器 - 捕获所有未处理的异常
    :param request: FastAPI请求对象
    :param exc: 异常对象
    :return: JSON响应
    """
    # 提取请求信息
    request_info = {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "client": (
            f"{request.client.host}:{request.client.port}"
            if request.client
            else "unknown"
        ),
    }

    # 尝试获取请求体（仅POST/PUT/PATCH）
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                # 限制请求体长度，避免日志过大
                body_str = body.decode("utf-8")[:500]
                request_info["body_preview"] = body_str
        except Exception:
            pass

    # 尝试获取查询参数
    if request.query_params:
        request_info["query_params"] = str(dict(request.query_params))

    # 安全地获取异常信息（避免 str(exc) 触发 SQLAlchemy 懒加载导致二次异常）
    try:
        exc_str = str(exc)
    except Exception:
        exc_str = f"<{type(exc).__name__}: str() failed>"

    # 记录异常到日志
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {exc_str}",
        exc_info=exc,
        extra={"request_info": request_info},
    )

    # 发送飞书告警（非阻塞）
    try:
        await send_alert(
            title="API异常告警",
            exc=exc,
            request_info=request_info,
            extra_info={
                "app": settings.APP_NAME,
                "environment": "Dev" if settings.DEBUG else "Prod",
            },
        )
    except Exception as e:
        logger.error(f"发送飞书告警失败: {str(e)}")

    # 返回统一的错误响应
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": BizError.INTERNAL_ERROR,
            "message": "服务器内部错误，请稍后重试",
            "detail": exc_str if logger.level <= 10 else None,  # DEBUG模式下显示详情
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    HTTP异常处理器 - 处理HTTP相关异常（4xx, 5xx）
    :param request: FastAPI请求对象
    :param exc: HTTP异常对象
    :return: JSON响应
    """
    # 只有服务器错误（5xx）才发送飞书告警
    if exc.status_code >= 500:
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "status_code": exc.status_code,
        }

        logger.error(
            f"HTTP {exc.status_code} Error: {exc.detail}",
            extra={"request_info": request_info},
        )

        # 发送飞书告警
        try:
            await send_alert(
                title=f"HTTP {exc.status_code} 错误",
                exc=Exception(exc.detail),
                request_info=request_info,
            )
        except Exception as e:
            logger.error(f"发送飞书告警失败: {str(e)}")

    # 如果是 BizException，使用其 code
    if isinstance(exc, BizException):
        code = exc.code
        message = exc.message
    else:
        code = BizError.BAD_REQUEST
        message = exc.detail

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": code,
            "message": message,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    请求验证异常处理器 - 处理Pydantic验证错误
    :param request: FastAPI请求对象
    :param exc: 验证异常对象
    :return: JSON响应
    """
    logger.warning(
        f"Validation error on {request.method} {request.url.path}: {exc.errors()}",
        extra={"errors": exc.errors()},
    )

    # 验证错误不发送飞书告警（太频繁）
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": BizError.VALIDATION_ERROR,
            "message": "请求参数验证失败",
            "detail": exc.errors(),
        },
    )
