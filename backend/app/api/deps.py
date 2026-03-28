# API依赖项

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..core.database import get_db, get_redis
from ..core.security import oauth2_scheme, decode_token, TokenData
from ..core.exceptions import BizException, BizError
from ..models.user import SystemUser, SystemRole, SystemMenu
from ..core.logging import get_logger

logger = get_logger(__name__)


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> SystemUser:
    """获取当前登录用户"""
    try:
        token_data = decode_token(token)
    except Exception as e:
        raise BizException(
            code=BizError.INVALID_CREDENTIALS,
            message="登录已过期，请重新登录",
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )
    if token_data is None:
        raise BizException(
            code=BizError.INVALID_CREDENTIALS,
            message="无法验证凭据",
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 查数据库
    result = await db.execute(
        select(SystemUser)
        .where(SystemUser.id == token_data.user_id)
        .options(selectinload(SystemUser.roles))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise BizException(
            code=BizError.USER_DOES_NOT_EXIST,
            message="用户不存在",
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise BizException(
            code=BizError.USER_DISABLED,
            message="用户已被禁用",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return user


async def get_current_active_user(
    current_user: SystemUser = Depends(get_current_user),
) -> SystemUser:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise BizException(
            code=BizError.USER_DISABLED,
            message="用户已被禁用",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return current_user


async def get_current_superuser(
    current_user: SystemUser = Depends(get_current_user),
) -> SystemUser:
    """获取当前超级用户"""
    roles = current_user.roles
    if not any(role.is_superuser for role in roles):
        raise BizException(
            code=BizError.PERMISSION_DENIED,
            message="权限不足",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return current_user


async def get_optional_user(
    db: AsyncSession = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[SystemUser]:
    """可选的用户认证（不强制登录）"""
    if not token:
        return None

    token_data = decode_token(token)
    if token_data is None:
        return None

    result = await db.execute(
        select(SystemUser)
        .where(SystemUser.id == token_data.user_id)
        .options(selectinload(SystemUser.roles))
    )
    return result.scalar_one_or_none()


CurrentUser = Annotated[SystemUser, Depends(get_current_user)]
CurrentActiveUser = Annotated[SystemUser, Depends(get_current_active_user)]
CurrentSuperUser = Annotated[SystemUser, Depends(get_current_superuser)]
OptionalUser = Annotated[Optional[SystemUser], Depends(get_optional_user)]
