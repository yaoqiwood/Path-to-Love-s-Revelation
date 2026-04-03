# 用户API端点

from typing import List, Optional
from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi import Depends

from ...core.log_decorator import log_operate
from ...core.security import Token
from ...models.user import SystemUser
from ...schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    UserPage,
    UserInfoResponse,
    RouterVO,
    TokenPermissionResponse,
    UserPasswordReset,
    UserPasswordChange,
)
from ..deps import CurrentUser, CurrentSuperUser
from ...services.user_service import UserServiceDep

router = APIRouter()


# ==================== Auth & Profile ====================


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@log_operate(title="用户注册", business_type=1)
async def register_user(
    request: Request,
    user_data: UserCreate,
    service: UserServiceDep,
):
    """用户注册"""
    return await service.register(user_data)


@router.post("/login", response_model=Token)
@log_operate(title="用户登录", business_type=0)
async def login(
    user_data: UserLogin,
    request: Request,
    service: UserServiceDep,
):
    """用户登录"""
    client_ip = request.client.host if request.client else ""
    return await service.login(user_data, client_ip=client_ip)


@router.post("/logout")
@log_operate(title="用户登出", business_type=0)
async def logout(request: Request):
    """用户登出"""
    return {"message": "操作成功"}


@router.get("/validate-token", response_model=TokenPermissionResponse)
async def validate_token(
    service: UserServiceDep,
    authorization: str | None = Header(default=None),
):
    """免鉴权校验 token，并返回用户来源及权限枚举"""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="缺少认证信息")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证信息")

    return await service.validate_token_permission(token.strip())


@router.get("/info", response_model=UserInfoResponse)
async def get_user_info(
    current_user: CurrentUser,
    service: UserServiceDep,
):
    """获取当前用户信息、角色和权限"""
    return await service.get_user_info(current_user)


@router.get("/routers", response_model=List[RouterVO])
async def get_routers(
    current_user: CurrentUser,
    service: UserServiceDep,
):
    """获取动态路由（基于RBAC）"""
    return await service.get_routers(current_user)


# ==================== User Management ====================


@router.get("/", response_model=UserPage)
async def list_users(
    current_user: CurrentUser,
    service: UserServiceDep,
    page: int = 1,
    page_size: int = 20,
    username: Optional[str] = None,
    enable_status: Optional[int] = None,
):
    """分页获取用户列表"""
    return await service.list_users(
        page=page,
        page_size=page_size,
        username=username,
        enable_status=enable_status,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_detail(
    user_id: int,
    current_user: CurrentSuperUser,
    service: UserServiceDep,
):
    """获取用户详情"""
    return await service.get_user(user_id)


@router.post("/", response_model=UserResponse)
@log_operate(title="新增用户", business_type=1)
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: CurrentSuperUser,
    service: UserServiceDep,
):
    """新增用户"""
    return await service.create_user(user_data, operator=current_user.username)


@router.put("/{user_id}", response_model=UserResponse)
@log_operate(title="编辑用户", business_type=2)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    current_user: CurrentSuperUser,
    service: UserServiceDep,
):
    """更新用户"""
    return await service.update_user(user_id, user_data, operator=current_user.username)


@router.delete("/{user_id}")
@log_operate(title="删除用户", business_type=3)
async def delete_user(
    user_id: int,
    request: Request,
    current_user: CurrentSuperUser,
    service: UserServiceDep,
):
    """删除用户 (软删除)"""
    return await service.delete_user(user_id, operator=current_user.username)


@router.put("/{user_id}/password")
@log_operate(title="重置用户密码", business_type=2)
async def reset_password(
    user_id: int,
    data: UserPasswordReset,
    request: Request,
    current_user: CurrentSuperUser,
    service: UserServiceDep,
):
    """重置用户密码"""
    return await service.reset_password(user_id, data, operator=current_user.username)


@router.post("/password")
@log_operate(title="修改个人信息", business_type=2)
async def change_password(
    data: UserPasswordChange,
    request: Request,
    current_user: CurrentUser,
    service: UserServiceDep,
):
    """修改个人密码"""
    return await service.change_password(current_user, data)
