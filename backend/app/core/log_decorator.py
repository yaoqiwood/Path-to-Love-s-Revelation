from functools import wraps
import time
import json
from typing import Optional, Callable

from fastapi import Request, Response
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from .database import SessionLocal
from ..models.system_log import SystemLogOperate
from ..core.logging import get_logger

logger = get_logger(__name__)


def log_operate(title: str, business_type: int = 0, operator_type: int = 0):
    """
    操作日志装饰器

    :param title: 模块标题
    :param business_type: 业务类型（0其它 1新增 2修改 3删除）
    :param operator_type: 操作类别（0其它 1后台用户 2手机端用户）
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取 Request 对象 (FastAPI 依赖注入通常会传递 Request)
            request: Optional[Request] = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                # 尝试从 kwargs 获取
                request = kwargs.get("request")

            # ★ 在调用端点函数之前，提前提取用户信息为普通 Python 值
            # 避免在 finally 中访问可能已过期的 SQLAlchemy 模型对象
            user_id = 0
            username = ""
            current_user = kwargs.get("current_user")
            if current_user and hasattr(current_user, "id"):
                user_id = current_user.id
                username = getattr(current_user, "username", "")
            elif (
                request and hasattr(request, "state") and hasattr(request.state, "user")
            ):
                user = request.state.user
                if user:
                    user_id = user.id
                    username = user.username

            start_time = time.time()
            error_msg = None
            status = 0  # 正常
            result = ""

            try:
                # 执行原函数
                response = await func(*args, **kwargs)
                return response
            except Exception as e:
                status = 1  # 异常
                error_msg = str(e)
                raise e
            finally:
                cost_time = int((time.time() - start_time) * 1000)

                if request:
                    try:
                        await save_log(
                            request=request,
                            user_id=user_id,
                            username=username,
                            title=title,
                            business_type=business_type,
                            operator_type=operator_type,
                            status=status,
                            error_msg=error_msg,
                            cost_time=cost_time,
                            result=result,
                        )
                    except Exception as ex:
                        logger.error(f"Failed to save operate log: {ex}")

        return wrapper

    return decorator


async def save_log(
    request: Request,
    user_id: int,
    username: str,
    title: str,
    business_type: int,
    operator_type: int,
    status: int,
    error_msg: str,
    cost_time: int,
    result: str,
):
    """保存日志到数据库"""

    # 获取请求体参数
    param = ""
    try:
        # 注意: 如果 request body 已经被读取，这里可能无法再次读取
        # 实际生产中通常在 middleware 中缓存 body
        # 这里简单尝试获取 query params 和 path params
        params_dict = dict(request.query_params)
        params_dict.update(request.path_params)
        param = json.dumps(params_dict, ensure_ascii=False)[:2000]
    except Exception as e:
        logger.error(f"Failed to get request params: {e}, {user_id}, {username}")

    log = SystemLogOperate(
        title=title,
        business_type=business_type,
        method=request.method,
        request_method=request.method,
        operator_type=operator_type,
        user_id=user_id,
        username=username,
        url=str(request.url),
        ip=request.client.host if request.client else "",
        param=param,
        result=result[:2000],
        status=status,
        error=error_msg[:2000] if error_msg else None,
        cost_time=cost_time,
    )

    # Database operation is async, can be awaited directly
    await _insert_log(log)


async def _insert_log(log: SystemLogOperate):
    async with SessionLocal() as db:
        try:
            db.add(log)
            await db.commit()
        except Exception as e:
            logger.error(f"Db error saving log: {e}")
            await db.rollback()
