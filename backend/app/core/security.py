# 安全模块 - JWT认证和密码处理

from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt, JWTError
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from .config import settings


# OAuth2密码认证方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/users/login")


class Token(BaseModel):
    """Token响应模型"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token数据模型"""

    user_id: Optional[int] = None
    username: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """解码和验证令牌"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        sub = payload.get("sub")
        username: str = payload.get("username")

        if sub is None:
            return None

        # 确保 user_id 是整数
        user_id = int(sub) if isinstance(sub, str) else sub

        return TokenData(user_id=user_id, username=username)
    except JWTError as e:
        print(f"JWT decode error: {e}")
        return None
    except Exception as e:
        print(f"Token decode error: {e}")
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前用户的依赖项"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception

    # 这里应该从数据库获取用户，暂时返回token数据
    # 后续会在deps.py中完善
    return token_data


def check_permission(required_permission: str):
    """权限检查装饰器工厂"""

    async def permission_checker(current_user=Depends(get_current_user)):
        # TODO: 实现权限检查逻辑
        # 检查用户是否有required_permission权限
        return current_user

    return permission_checker
